#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Tuple
import requests
from urllib.parse import quote

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_PAGE_BASE = "https://en.wikipedia.org/wiki/"
ROBOTS_URL = "https://en.wikipedia.org/robots.txt"

def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def whitespace_token_count(text: str) -> int:
    # Your schema says whitespace-split tokens
    return len(text.split())

def build_page_url(title: str) -> str:
    # Wikipedia article URLs are title with spaces -> underscores, then URL-encoded
    return WIKI_PAGE_BASE + quote(title.replace(" ", "_"), safe="()!$&'*,;=@:+/?-._~")

def fetch_robots_txt(session: requests.Session, user_agent: str) -> Optional[str]:
    try:
        r = session.get(ROBOTS_URL, headers={"User-Agent": user_agent}, timeout=20)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return None

def get_category_members(
    session: requests.Session,
    category: str,
    limit: int,
    user_agent: str,
    sleep_s: float,
) -> List[str]:
    """
    Returns up to `limit` page titles from a Wikipedia category.
    category should be like "Category:Machine_learning"
    """
    titles: List[str] = []
    cmcontinue = None

    while len(titles) < limit:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": min(500, limit - len(titles)),
            "cmtype": "page",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        r = session.get(WIKI_API, params=params, headers={"User-Agent": user_agent}, timeout=30)
        r.raise_for_status()
        data = r.json()

        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            t = m.get("title")
            if t:
                titles.append(t)
                if len(titles) >= limit:
                    break

        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break

        time.sleep(sleep_s)

    return titles

def fetch_extract_plaintext(
    session: requests.Session,
    title: str,
    user_agent: str,
) -> Tuple[int, str]:
    """
    Returns (status_code, plaintext_extract).
    If no extract found, plaintext_extract may be empty.
    """
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "exsectionformat": "plain",
        "titles": title,
        "format": "json",
        "redirects": 1,  # follow redirects
    }

    r = session.get(WIKI_API, params=params, headers={"User-Agent": user_agent}, timeout=30)
    status = r.status_code
    if status != 200:
        return status, ""

    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    # pages is dict keyed by pageid as string
    for _, page in pages.items():
        extract = page.get("extract", "")
        return status, extract or ""

    return status, ""

def record_for_title(
    title: str,
    run_id: str,
    robots_txt: Optional[str],
    session: requests.Session,
    user_agent: str,
) -> dict:
    # requested_url: the page URL we intended to fetch (your schema)
    requested_url = build_page_url(title)

    # We fetch via API, but your schema wants "fetched_url = URL request actually reached".
    # We can treat fetched_url as the final canonical page URL for identity/logging purposes.
    # (API response URL isn't that useful.)
    fetched_url = requested_url  # Wikipedia API follows redirects internally; keep canonical-ish URL.

    status_code, raw_text = fetch_extract_plaintext(session, title, user_agent=user_agent)

    # content_hash: sha256 of raw_content (as per your required field)
    content_hash = sha256_hex(raw_text)

    # id format you specified: "{hash of fetched_url}_{timestamp}"
    timestamp = iso_now()
    fetched_url_hash = sha256_hex(fetched_url)
    record_id = f"{fetched_url_hash}_{timestamp}"

    rec = {
        "id": record_id,
        "run_id": run_id,
        "timestamp": timestamp,
        "source": "wikipedia",
        "content_type": "Web",
        "requested_url": requested_url,
        "fetched_url": fetched_url,
        "status_code": int(status_code),
        "length": whitespace_token_count(raw_text),
        "raw_content": raw_text,
        "content_format": "plaintext",
        "content_hash": content_hash,
    }

    # Optional fields
    rec["title"] = title
    rec["language"] = "en"  # you said you're starting with Wikipedia en
    # Wikipedia content licensing is CC BY-SA 4.0 + GFDL; keep it simple if your schema wants one.
    rec["license_type"] = "CC-BY-SA"
    rec["license"] = "CC-BY-SA-4.0"
    if robots_txt is not None:
        rec["robots_txt_content"] = robots_txt

    return rec

def load_titles_file(path: str) -> List[str]:
    titles: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t and not t.startswith("#"):
                titles.append(t)
    return titles

def main():
    ap = argparse.ArgumentParser(description="Ingest Wikipedia plaintext into JSONL (raw schema).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--titles-file", type=str, help="Path to file with one Wikipedia page title per line.")
    g.add_argument("--category", type=str, help='Wikipedia category, e.g. "Category:Machine_learning"')
    ap.add_argument("--limit", type=int, default=100, help="Max pages to ingest (category mode).")
    ap.add_argument("--out", type=str, default="wikipedia_raw.jsonl", help="Output JSONL path.")
    ap.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between API calls.")
    ap.add_argument(
        "--user-agent",
        type=str,
        default="SotonLM-DataEngineering/0.1 (contact: data-eng@sotonlm)",
        help="User-Agent header (set something real).",
    )
    ap.add_argument("--include-robots", action="store_true", help="Fetch and include robots.txt content (optional field).")
    args = ap.parse_args()

    run_id = f"wiki_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    session = requests.Session()

    robots_txt = None
    if args.include_robots:
        robots_txt = fetch_robots_txt(session, args.user_agent)

    if args.titles_file:
        titles = load_titles_file(args.titles_file)
    else:
        titles = get_category_members(
            session=session,
            category=args.category,
            limit=args.limit,
            user_agent=args.user_agent,
            sleep_s=args.sleep,
        )

    with open(args.out, "w", encoding="utf-8") as f:
        for i, title in enumerate(titles, start=1):
            rec = record_for_title(
                title=title,
                run_id=run_id,
                robots_txt=robots_txt,
                session=session,
                user_agent=args.user_agent,
            )
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if args.sleep > 0:
                time.sleep(args.sleep)

    print(f"Wrote {len(titles)} records to {args.out} (run_id={run_id})")

if __name__ == "__main__":
    main()