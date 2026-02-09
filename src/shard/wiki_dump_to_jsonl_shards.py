#!/usr/bin/env python3
"""
Stream-parse a Wikipedia pages-articles XML dump (.xml.bz2) into uncompressed JSONL shards (~512 MiB each),
with a bounded shuffle buffer to avoid alphabetical shard bias.

Usage example:
  python3 wiki_dump_to_jsonl_shards.py \
    --dump enwiki-latest-pages-articles.xml.bz2 \
    --out-dir data/raw/web \
    --max-pages 0 \
    --shard-mib 512 \
    --buffer-size 10000 \
    --seed 42
"""

import argparse
import bz2
import datetime as dt
import hashlib
import json
import os
import random
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple

MiB = 1024 * 1024


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def make_run_id(prefix: str = "enwiki") -> str:
    return f"{prefix}_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_dump"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def canonical_wikipedia_url(title: str, lang: str = "en") -> str:
    # Wikipedia canonical URL encoding is more complex for special chars; this is "good enough" for titles.
    # If you want exact encoding, do urllib.parse.quote with safe="()_/:"
    return f"https://{lang}.wikipedia.org/wiki/" + title.replace(" ", "_")


def strip_ns(tag: str) -> str:
    # "{namespace}tag" -> "tag"
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def iter_wikipedia_pages(dump_bz2_path: str) -> Iterator[Dict]:
    """
    Stream parse XML and yield page dict:
      title, ns, page_id, is_redirect, revision_id, revision_ts, text
    """
    # ElementTree iterparse supports file-like objects; bz2.open returns one.
    with bz2.open(dump_bz2_path, "rb") as f:
        context = ET.iterparse(f, events=("end",))
        for event, elem in context:
            if strip_ns(elem.tag) != "page":
                continue

            # Extract page fields
            title = ""
            ns = 0
            page_id = 0
            is_redirect = False
            revision_id = 0
            revision_ts = None
            text = ""

            # Iterate children to avoid repeated .find with namespaces
            revision_elem = None
            for child in list(elem):
                name = strip_ns(child.tag)
                if name == "title":
                    title = child.text or ""
                elif name == "ns":
                    try:
                        ns = int(child.text or "0")
                    except ValueError:
                        ns = 0
                elif name == "id":
                    # first <id> under <page> is page_id
                    if page_id == 0:
                        try:
                            page_id = int(child.text or "0")
                        except ValueError:
                            page_id = 0
                elif name == "redirect":
                    # <redirect title="..."/>
                    is_redirect = True
                elif name == "revision":
                    revision_elem = child

            # Revision details (latest revision in pages-articles dumps)
            if revision_elem is not None:
                for rchild in list(revision_elem):
                    rname = strip_ns(rchild.tag)
                    if rname == "id":
                        try:
                            revision_id = int(rchild.text or "0")
                        except ValueError:
                            revision_id = 0
                    elif rname == "timestamp":
                        revision_ts = rchild.text
                    elif rname == "text":
                        text = rchild.text or ""

            yield {
                "title": title,
                "ns": ns,
                "page_id": page_id,
                "is_redirect": is_redirect,
                "revision_id": revision_id,
                "revision_ts": revision_ts,
                "text": text,
            }

            # Free memory aggressively
            elem.clear()


class JsonlShardWriter:
    def __init__(self, out_dir: Path, prefix: str, shard_target_bytes: int):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.shard_target_bytes = shard_target_bytes

        self.shard_index = 0
        self.bytes_written = 0
        self.records_written = 0
        self.current_path: Optional[Path] = None
        self.fh = None

        self.shard_stats = []  # list of dicts: {file, bytes, records}

        self._open_new()

    def _open_new(self) -> None:
        if self.fh is not None:
            self.fh.close()
            # finalize stats for previous shard
            self.shard_stats.append(
                {
                    "file": str(self.current_path.name),
                    "bytes": self.bytes_written,
                    "records": self.records_written,
                }
            )

        self.current_path = self.out_dir / f"{self.prefix}_{self.shard_index:06d}.jsonl"
        self.fh = open(self.current_path, "wb")
        self.shard_index += 1
        self.bytes_written = 0
        self.records_written = 0

    def write_obj(self, obj: Dict) -> None:
        line = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        if self.bytes_written + len(line) > self.shard_target_bytes and self.bytes_written > 0:
            self._open_new()
        self.fh.write(line)
        self.bytes_written += len(line)
        self.records_written += 1

    def close(self) -> None:
        if self.fh is not None:
            self.fh.close()
            self.shard_stats.append(
                {
                    "file": str(self.current_path.name),
                    "bytes": self.bytes_written,
                    "records": self.records_written,
                }
            )
            self.fh = None


def build_raw_record(
    page: Dict,
    run_id: str,
    dump_file: str,
    lang: str = "en",
    division: str = "web",
    source: str = "wikipedia",
) -> Dict:
    title = page["title"]
    page_id = page["page_id"]
    revision_id = page["revision_id"]
    revision_ts = page["revision_ts"]
    ns = page["ns"]
    raw_content = page["text"]

    url = canonical_wikipedia_url(title, lang=lang)

    record = {
        # Stable doc identity: wikipedia:<page_id>
        "id": f"wikipedia:{page_id}",
        "run_id": run_id,
        "timestamp": utc_now_iso(),  # processing time; revision time goes in meta
        "division": division,
        "source": source,
        "url": url,
        "raw_content": raw_content,
        "content_format": "wikitext",
        "content_sha256": sha256_text(raw_content),
        "length_tokens": len(raw_content.split()),
        "meta": {
            "page_id": page_id,
            "revision_id": revision_id,
            "title": title,
            "namespace": ns,
            "revision_timestamp": revision_ts,
            "dump_file": dump_file,
            "license": "CC BY-SA 4.0",
        },
    }
    return record


def write_manifest(out_dir: Path, manifest: Dict) -> None:
    path = out_dir / "manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True, help="Path to Wikipedia dump .xml.bz2")
    ap.add_argument("--out-dir", required=True, help="Base output directory (run folder will be created inside)")
    ap.add_argument("--lang", default="en", help="Wiki language code (default: en)")
    ap.add_argument("--shard-mib", type=int, default=512, help="Target shard size in MiB (uncompressed JSONL bytes)")
    ap.add_argument("--buffer-size", type=int, default=10000, help="Shuffle buffer size (docs). 0 disables shuffling.")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for deterministic shuffling")
    ap.add_argument("--max-pages", type=int, default=0, help="Stop after N pages seen (0 = full dump)")
    ap.add_argument("--min-tokens", type=int, default=20, help="Drop docs shorter than this (whitespace tokens)")
    ap.add_argument("--prefix", default="wikipedia", help="Shard filename prefix")
    args = ap.parse_args()

    dump_path = Path(args.dump)
    if not dump_path.exists():
        print(f"ERROR: dump not found: {dump_path}", file=sys.stderr)
        return 2

    run_id = make_run_id(prefix=f"{args.lang}wiki")
    run_dir = Path(args.out_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    shard_target_bytes = args.shard_mib * MiB
    writer = JsonlShardWriter(run_dir, prefix=args.prefix, shard_target_bytes=shard_target_bytes)

    rng = random.Random(args.seed)
    buffer = []

    # Stats
    start = time.time()
    pages_seen = 0
    kept_articles = 0
    dropped_non_article_namespace = 0
    dropped_redirects = 0
    dropped_too_short_or_empty = 0

    dump_file = dump_path.name

    last_report_t = start
    last_report_seen = 0

    try:
        for page in iter_wikipedia_pages(str(dump_path)):
            pages_seen += 1
            if args.max_pages and pages_seen > args.max_pages:
                break

            # Filter: namespace 0 only
            if page["ns"] != 0:
                dropped_non_article_namespace += 1
                continue

            # Filter: redirects
            if page["is_redirect"]:
                dropped_redirects += 1
                continue

            text = page["text"].strip()
            if not text:
                dropped_too_short_or_empty += 1
                continue

            # Filter: very short
            tok_len = len(text.split())
            if tok_len < args.min_tokens:
                dropped_too_short_or_empty += 1
                continue

            obj = build_raw_record(page, run_id=run_id, dump_file=dump_file, lang=args.lang)
            kept_articles += 1

            if args.buffer_size and args.buffer_size > 0:
                buffer.append(obj)
                if len(buffer) >= args.buffer_size:
                    rng.shuffle(buffer)
                    for rec in buffer:
                        writer.write_obj(rec)
                    buffer.clear()
            else:
                writer.write_obj(obj)

            # Progress report every ~10s
            now = time.time()
            if now - last_report_t >= 10:
                delta = pages_seen - last_report_seen
                rate = delta / (now - last_report_t)
                print(f"[INFO] pages_seen={pages_seen:,} kept={kept_articles:,} rate={rate:,.1f} pages/s")
                last_report_t = now
                last_report_seen = pages_seen

        # Flush remaining buffer
        if buffer:
            rng.shuffle(buffer)
            for rec in buffer:
                writer.write_obj(rec)
            buffer.clear()

    finally:
        writer.close()

    elapsed = time.time() - start

    manifest = {
        "run_id": run_id,
        "created_at": utc_now_iso(),
        "input_dump": str(dump_path.resolve()),
        "dump_file": dump_file,
        "settings": {
            "lang": args.lang,
            "shard_target_mib": args.shard_mib,
            "shard_target_bytes": shard_target_bytes,
            "shuffle_buffer_size": args.buffer_size,
            "seed": args.seed,
            "max_pages": args.max_pages,
            "min_tokens": args.min_tokens,
        },
        "stats": {
            "total_pages_seen": pages_seen,
            "kept_articles": kept_articles,
            "dropped_non_article_namespace": dropped_non_article_namespace,
            "dropped_redirects": dropped_redirects,
            "dropped_too_short_or_empty": dropped_too_short_or_empty,
            "elapsed_seconds": round(elapsed, 2),
        },
        "shards": writer.shard_stats,
    }
    write_manifest(run_dir, manifest)

    print("\nDone.")
    print(f"Output: {run_dir.resolve()}")
    print(f"Manifest: {(run_dir / 'manifest.json').resolve()}")
    print(json.dumps(manifest["stats"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
