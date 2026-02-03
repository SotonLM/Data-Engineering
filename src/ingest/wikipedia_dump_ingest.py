#!/usr/bin/env python3
"""
Wikipedia dump ingester -> sharded JSONL (optionally zstd compressed).

Pipeline:
- (optional) download enwiki pages-articles dump
- stream parse XML
- keep ns=0 (articles)
- drop redirects
- extract wikitext
- optionally convert to plaintext
- write JSONL shards: out_dir/<run_id>/wikipedia_<shard_idx>.jsonl(.zst)

Notes:
- This is designed for long-running jobs on a server.
- It does not load the dump into memory.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple

import xml.etree.ElementTree as ET

# Optional deps
try:
    import mwparserfromhell
except ImportError:
    mwparserfromhell = None

try:
    import zstandard as zstd
except ImportError:
    zstd = None

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


DEFAULT_DUMP_URL = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2"

# Wikipedia XML namespaces are sometimes present; we handle both cases.
NS_RE = re.compile(r"^\{.*\}")


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_hex_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def whitespace_token_count(text: str) -> int:
    return len(text.split())


def normalize_title_to_url(title: str, lang: str = "en") -> str:
    # Wikipedia canonical-ish article URL for identity/audit
    # (not perfect, but good enough)
    t = title.replace(" ", "_")
    # minimal escaping
    t = t.replace("%", "%25")
    return f"https://{lang}.wikipedia.org/wiki/{t}"


def strip_xml_ns(tag: str) -> str:
    return NS_RE.sub("", tag)


def is_redirect_wikitext(wikitext: str) -> bool:
    # Wikipedia redirects usually start with "#REDIRECT" (case-insensitive) at beginning
    head = wikitext.lstrip()[:40].lower()
    return head.startswith("#redirect")


def wikitext_to_plaintext(wikitext: str) -> str:
    """
    Convert MediaWiki wikitext to rough plaintext.
    This is not perfect, but good enough for initial corpus.
    """
    if mwparserfromhell is None:
        raise RuntimeError("mwparserfromhell is not installed. Install it or run with --keep-wikitext.")

    code = mwparserfromhell.parse(wikitext)

    # Remove common noisy elements
    for tpl in code.filter_templates(recursive=True):
        # Strip templates entirely (infoboxes, navboxes, etc.)
        try:
            code.remove(tpl)
        except Exception:
            pass

    for tag in code.filter_tags(recursive=True):
        try:
            code.remove(tag)
        except Exception:
            pass

    text = code.strip_code(normalize=True, collapse=True)

    # Cleanup
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


@dataclass
class ShardWriter:
    out_dir: Path
    run_id: str
    compress: bool
    shard_docs: int

    shard_idx: int = 0
    docs_in_shard: int = 0
    fh = None
    zctx = None

    def _open_new(self) -> None:
        self.close()

        self.out_dir.mkdir(parents=True, exist_ok=True)

        base = self.out_dir / self.run_id
        base.mkdir(parents=True, exist_ok=True)

        name = f"wikipedia_{self.shard_idx:05d}.jsonl"
        path = base / (name + (".zst" if self.compress else ""))

        if self.compress:
            if zstd is None:
                raise RuntimeError("zstandard is not installed. Install it or run without --compress-zst.")
            # stream writer
            self.fh = open(path, "wb")
            self.zctx = zstd.ZstdCompressor(level=10).stream_writer(self.fh)
        else:
            self.fh = open(path, "w", encoding="utf-8")
            self.zctx = None

        self.docs_in_shard = 0

    def write_obj(self, obj: Dict) -> None:
        if self.fh is None:
            self._open_new()

        line = json.dumps(obj, ensure_ascii=False) + "\n"

        if self.compress:
            assert self.zctx is not None
            self.zctx.write(line.encode("utf-8"))
        else:
            self.fh.write(line)

        self.docs_in_shard += 1

        if self.docs_in_shard >= self.shard_docs:
            self.rotate()

    def rotate(self) -> None:
        self.close()
        self.shard_idx += 1
        self._open_new()

    def close(self) -> None:
        if self.compress and self.zctx is not None:
            try:
                self.zctx.flush(zstd.FLUSH_FRAME)
            except Exception:
                pass
            try:
                self.zctx.close()
            except Exception:
                pass
            self.zctx = None

        if self.fh is not None:
            try:
                self.fh.close()
            except Exception:
                pass
            self.fh = None


def download_file(url: str, out_path: Path) -> None:
    """
    Download using urllib (no external tools), with resume by temp file rename.
    """
    import urllib.request

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")

    req = urllib.request.Request(url, headers={"User-Agent": "SotonLM-DataEngineering/0.1"})
    with urllib.request.urlopen(req) as resp, open(tmp_path, "wb") as f:
        shutil.copyfileobj(resp, f)

    tmp_path.replace(out_path)


def iter_wikipedia_pages(dump_bz2_path: Path) -> Iterator[Tuple[str, int, int, str]]:
    """
    Stream parse Wikipedia pages from .xml.bz2.
    Yields: (title, ns, page_id, wikitext)
    """
    # Stream decompress
    with bz2.open(dump_bz2_path, "rb") as f:
        # iterparse emits events without loading entire XML
        context = ET.iterparse(f, events=("end",))
        title = None
        ns = None
        page_id = None
        text = None

        # We parse per <page> end
        for event, elem in context:
            tag = strip_xml_ns(elem.tag)

            if tag == "title":
                title = elem.text or ""
            elif tag == "ns":
                try:
                    ns = int((elem.text or "0").strip())
                except ValueError:
                    ns = None
            elif tag == "id":
                # There are multiple <id> tags (page id, revision id, contributor id).
                # We only want the page <id>, which is a direct child of <page>.
                parent = elem.getparent() if hasattr(elem, "getparent") else None
                # ElementTree in stdlib doesn't provide parent pointers.
                # So we handle page_id differently below using a safer approach:
                pass
            elif tag == "text":
                text = elem.text or ""
            elif tag == "page":
                # Extract page_id and revision_id by searching children explicitly
                # because stdlib ElementTree lacks parent pointers.
                page_id_node = elem.find("./id")
                page_id_val = int(page_id_node.text) if page_id_node is not None and page_id_node.text else -1

                # title/ns/text already captured, but safer to fetch from elem too
                title_node = elem.find("./title")
                ns_node = elem.find("./ns")
                rev_text_node = elem.find("./revision/text")

                title_val = (title_node.text or "") if title_node is not None else (title or "")
                ns_val = int(ns_node.text) if ns_node is not None and ns_node.text else (ns if ns is not None else -1)
                text_val = (rev_text_node.text or "") if rev_text_node is not None else (text or "")

                yield (title_val, ns_val, page_id_val, text_val)

                # Critical: clear element to free memory
                elem.clear()
                title, ns, page_id, text = None, None, None, None


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest Wikipedia dumps into sharded JSONL (optional zstd).")
    ap.add_argument("--dump-path", type=str, default="", help="Path to local enwiki pages-articles .xml.bz2")
    ap.add_argument("--download", action="store_true", help="Download the dump if --dump-path not provided.")
    ap.add_argument("--dump-url", type=str, default=DEFAULT_DUMP_URL, help="Dump URL to download.")
    ap.add_argument("--out-dir", type=str, default="data/raw/web", help="Base output dir (repo-relative OK).")
    ap.add_argument("--run-id", type=str, default="", help="Run id. Default: enwiki_<UTC timestamp>.")
    ap.add_argument("--lang", type=str, default="en", help="Wiki language (default en).")
    ap.add_argument("--keep-wikitext", action="store_true", help="Store wikitext instead of plaintext.")
    ap.add_argument("--drop-redirects", action="store_true", default=True, help="Drop redirect pages (default true).")
    ap.add_argument("--keep-redirects", action="store_true", help="Keep redirects (overrides --drop-redirects).")
    ap.add_argument("--min-tokens", type=int, default=50, help="Drop docs with fewer than this many whitespace tokens.")
    ap.add_argument("--shard-docs", type=int, default=500, help="Docs per shard.")
    ap.add_argument("--compress-zst", action="store_true", help="Write .jsonl.zst shards (recommended).")
    ap.add_argument("--max-pages", type=int, default=2000, help="Stop after N pages (0 = no limit).")
    args = ap.parse_args()

    # Safety default: limit pages so test runs finish quickly.
    if args.max_pages:
        print(f"[INFO] Running in limited mode: max_pages={args.max_pages}")

    # Resolve paths robustly regardless of CWD
    repo_cwd = Path.cwd()
    out_dir = (repo_cwd / args.out_dir).resolve()

    run_id = args.run_id.strip() or f"{args.lang}wiki_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_dump"
    timestamp = iso_now()

    if args.keep_redirects:
        drop_redirects = False
    else:
        drop_redirects = True  # default

    dump_path = Path(args.dump_path).expanduser()
    if not dump_path and not args.download:
        print("ERROR: Provide --dump-path or use --download", file=sys.stderr)
        sys.exit(1)

    if args.download:
        dump_path = dump_path if dump_path else Path(f"{args.lang}wiki-pages-articles.xml.bz2")
        dump_path = dump_path.resolve()
        if dump_path.exists():
            print(f"Dump already exists at: {dump_path}")
        else:
            print(f"Downloading dump to: {dump_path}")
            download_file(args.dump_url, dump_path)

    if not dump_path.exists():
        print(f"ERROR: dump file not found: {dump_path}", file=sys.stderr)
        sys.exit(1)

    if not args.keep_wikitext and mwparserfromhell is None:
        print("ERROR: mwparserfromhell not installed. Install it or run with --keep-wikitext", file=sys.stderr)
        sys.exit(1)

    writer = ShardWriter(out_dir=out_dir, run_id=run_id, compress=args.compress_zst, shard_docs=args.shard_docs)

    total = 0
    kept = 0
    dropped_ns = 0
    dropped_redirect = 0
    dropped_short = 0

    iterator = iter_wikipedia_pages(dump_path)

    if tqdm is not None:
        iterator = tqdm(iterator, desc="Parsing pages", unit="page")

    try:
        for title, ns, page_id, wikitext in iterator:
            total += 1
            if args.max_pages and total > args.max_pages:
                break

            # Keep only main namespace (articles)
            if ns != 0:
                dropped_ns += 1
                continue

            if drop_redirects and is_redirect_wikitext(wikitext):
                dropped_redirect += 1
                continue

            if args.keep_wikitext:
                content = (wikitext or "").strip()
                content_format = "wikitext"
            else:
                content = wikitext_to_plaintext(wikitext or "")
                content_format = "plaintext"

            if not content:
                dropped_short += 1
                continue

            length_tokens = whitespace_token_count(content)
            if length_tokens < args.min_tokens:
                dropped_short += 1
                continue

            url = normalize_title_to_url(title, lang=args.lang)
            final_url = url  # dump-based; no runtime redirects
            status_code = 200  # dump-based; not fetched via HTTP per page

            # Identity: stable per article (best)
            stable_id = f"wikipedia:{page_id}"

            # If your pipeline insists on hashed ID, hash the stable identity string:
            # id_val = sha256_hex_str(stable_id)
            id_val = stable_id

            content_sha256 = sha256_hex_str(content)

            obj = {
                # Required-ish fields you've been discussing
                "id": id_val,
                "run_id": run_id,
                "timestamp": timestamp,

                # Your naming (division/source)
                "division": "web",
                "source": "wikipedia",

                "url": url,
                "final_url": final_url,
                "status_code": status_code,

                "raw_content": content,
                "content_format": content_format,

                "length_tokens": length_tokens,
                "content_sha256": content_sha256,

                # Always keep provenance
                "meta": {
                    "page_id": page_id,
                    "title": title,
                    "namespace": ns,
                    "dump_path": str(dump_path),
                    "dump_url": args.dump_url if args.download else None,
                    "license": "CC-BY-SA-4.0",
                },
            }

            writer.write_obj(obj)
            kept += 1

    finally:
        writer.close()

    # Write a simple run manifest
    manifest = {
        "run_id": run_id,
        "created_at": timestamp,
        "dump_path": str(dump_path),
        "dump_url": args.dump_url if args.download else None,
        "out_dir": str(out_dir / run_id),
        "stats": {
            "total_pages_seen": total,
            "kept_articles": kept,
            "dropped_non_article_namespace": dropped_ns,
            "dropped_redirects": dropped_redirect,
            "dropped_too_short_or_empty": dropped_short,
        },
        "settings": {
            "lang": args.lang,
            "keep_wikitext": args.keep_wikitext,
            "drop_redirects": drop_redirects,
            "min_tokens": args.min_tokens,
            "shard_docs": args.shard_docs,
            "compress_zst": args.compress_zst,
        },
    }

    manifest_path = (out_dir / run_id / "manifest.json").resolve()
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nDone.")
    print(f"Output: {out_dir / run_id}")
    print(f"Manifest: {manifest_path}")
    print(json.dumps(manifest["stats"], indent=2))


if __name__ == "__main__":
    main()