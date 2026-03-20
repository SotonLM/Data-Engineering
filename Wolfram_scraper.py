"""
Wolfram Community Forum Scraper
================================
Scrapes discussions from community.wolfram.com and outputs a .jsonl file
where each line is one post, matching the team's clean data schema (v1).

Output fields per record:
    id, source, subsource, lang, length_tokens, quality_score,
    text, timestamp, title, url

Usage:
    pip install requests beautifulsoup4
    python wolfram_scraper.py
"""

import json
import time
import hashlib
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# ── Configuration ────────────────────────────────────────────────────────────

BASE_URL = "https://community.wolfram.com"

# Discussion list URL — we just change the page number at the end
# This fetches all discussions across all groups, sorted by most active
DISCUSSION_LIST_URL = (
    "https://community.wolfram.com/dashboard/-/discussions-list/"
    "all+groups/Any+discussions/none/active/full/20/{page}/filter"
)

OUTPUT_FILE = Path("wolfram_raw.jsonl")

# How many pages of the discussion list to scrape
# Each page has 20 threads — start small while testing
MAX_PAGES = 20

# Polite delay between requests (seconds)
REQUEST_DELAY = 1.5

# Minimum token count — skip very short posts
MIN_TOKENS = 20


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_page(url: str) -> BeautifulSoup | None:
    """
    Fetch a URL and return a BeautifulSoup object for parsing.
    Returns None if the request fails.
    """
    headers = {
        "User-Agent": "SotonLM-Scraper/1.0 (university AI research project)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [!] Failed to fetch {url}: {e}")
        return None


def make_id(url: str) -> str:
    """
    Generate a unique ID for a record from its URL.
    Format: academic_wolfram_{hash}
    """
    short_hash = hashlib.sha1(url.encode()).hexdigest()[:10]
    return f"academic_wolfram_{short_hash}"


def count_tokens(text: str) -> int:
    """
    Count whitespace-split tokens, matching the schema definition.
    """
    return len(text.split())


def clean_text(raw: str) -> str:
    """
    Basic text cleaning:
    - Strip leading/trailing whitespace per line
    - Collapse multiple blank lines into one
    """
    lines = raw.splitlines()
    result = []
    prev_blank = False
    for line in lines:
        line = line.strip()
        if line == "":
            if not prev_blank:
                result.append(line)
            prev_blank = True
        else:
            result.append(line)
            prev_blank = False
    return "\n".join(result).strip()


# ── Scraping Logic ────────────────────────────────────────────────────────────

def get_thread_urls(max_pages: int) -> list[str]:
    """
    Scrape the discussion list pages and return a list of thread URLs.

    We filter links to only keep ones matching the thread pattern:
        /groups/-/m/t/{number}
    This avoids picking up user profile links, tag links, etc.
    """
    thread_urls = []

    for page in range(1, max_pages + 1):
        url = DISCUSSION_LIST_URL.format(page=page)
        print(f"  Scanning discussion list page {page}: {url}")
        soup = get_page(url)
        if soup is None:
            break

        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            # Only keep links that match the thread URL pattern
            if "/groups/-/m/t/" in href:
                # Ensure it's a full URL
                full_url = href if href.startswith("http") else BASE_URL + href
                # Strip any query parameters
                full_url = full_url.split("?")[0]
                if full_url not in thread_urls:
                    thread_urls.append(full_url)

        time.sleep(REQUEST_DELAY)

    return thread_urls


def scrape_thread(thread_url: str) -> list[dict]:
    """
    Given a thread URL, extract all posts and return them as a list
    of records matching the clean data schema.

    Each post becomes its own record (one JSON line in the output).
    """
    soup = get_page(thread_url)
    if soup is None:
        return []

    records = []

    # Title is in the <h1> tag
    title_tag = soup.find("h1")
    thread_title = title_tag.get_text(strip=True) if title_tag else None

    # Wolfram Community wraps each post in a <div> with class containing "message"
    # We try a few common patterns to be safe
    posts = (
        soup.find_all("div", class_=lambda c: c and "message-body" in (c or ""))
        or soup.find_all("div", class_=lambda c: c and "post-body" in (c or ""))
        or soup.find_all("article")
    )

    # Fallback: if no post containers found, treat the whole page body as one record
    # This handles pages where content isn't wrapped in obvious post divs
    if not posts:
        body = soup.find("div", id="content") or soup.find("main") or soup.find("body")
        if body:
            posts = [body]

    for post in posts:
        raw_text = post.get_text(separator="\n")
        text = clean_text(raw_text)

        token_count = count_tokens(text)
        if token_count < MIN_TOKENS:
            continue

        # Try to find a timestamp in a <time> tag
        time_tag = post.find("time")
        timestamp = None
        if time_tag and time_tag.get("datetime"):
            timestamp = time_tag["datetime"]

        record = {
            "id": make_id(thread_url + text[:50]),
            "source": "academic",
            "subsource": "wolfram",
            "lang": "en",
            "length_tokens": token_count,
            "quality_score": 1.0,
            "text": text,
            "timestamp": timestamp,
            "title": thread_title,
            "url": thread_url,
        }
        records.append(record)

    return records


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Wolfram Community Scraper starting — output: {OUTPUT_FILE}\n")
    total_records = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as f_out:

        print("── Fetching thread list ──")
        thread_urls = get_thread_urls(MAX_PAGES)
        print(f"\nFound {len(thread_urls)} threads\n")

        for i, thread_url in enumerate(thread_urls, 1):
            print(f"[{i}/{len(thread_urls)}] Scraping: {thread_url}")
            records = scrape_thread(thread_url)

            for record in records:
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

            total_records += len(records)
            print(f"  → {len(records)} posts extracted")

            time.sleep(REQUEST_DELAY)

    print(f"\n✓ Done. {total_records} records written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
