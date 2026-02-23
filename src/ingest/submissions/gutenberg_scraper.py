"""
Gutenberg Text Harvester

Fetches a small number of Project Gutenberg books, (Just for testing as stated in instruction but can just loop through all page nums to do all)
removes license/header/footer text,

"""

import requests
import re
import time, random
import json
import hashlib
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


import requests
import re
import time
import random


def harvest_text(book_id):
    # Official cache mirror (much more reliable)
    target_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

    headers = {
        "User-Agent": "SotonLM-Test (your_email@example.com)"
    }

    try:
        r = requests.get(target_url, headers=headers, timeout=15)

        if r.status_code == 200:
            rawtext = r.text
            cleaned = strip_gutenberg_headers(rawtext)
            return cleaned
            #print_first_n_lines(cleaned, 20)

        else:
            print(f"Failed {book_id} (status {r.status_code})")

        # Be polite to Gutenberg servers
        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"Error fetching {book_id}: {e}")
        

def strip_gutenberg_headers(raw_text):
    """
    Strips Project Gutenberg header and footer from the raw text of a book.
    """
    lines = raw_text.splitlines()
    start_idx = 0
    end_idx = len(lines)

    # Loop through lines to find start and end markers
    for i, line in enumerate(lines):
        upper_line = line.upper()
        if upper_line.startswith("*** START OF"):
            start_idx = i + 1
        elif upper_line.startswith("*** END OF"):
            end_idx = i
            break

    # Extract only the lines between start and end
    content_lines = lines[start_idx:end_idx]

    # Remove empty lines at the beginning and end
    while content_lines and not content_lines[0].strip():
        content_lines.pop(0)
    while content_lines and not content_lines[-1].strip():
        content_lines.pop()

    clean_text = content_lines

    # Now getting where actual beginning is
    for idx, line in enumerate(content_lines):
        if looks_like_paragraph(line):
            clean_text = content_lines[idx::]
            break

    return final_clean(("\n".join(clean_text)).strip())


def final_clean(raw_text):
    """
    Removing trailing spaces
    Collapsing multiple blank lines to a single blank line
    Keeping only ASCII printable characters
    """

    clean_text = "\n".join(line.strip() for line in raw_text.splitlines())
    clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)  # replace multiple empty lines with just two newlines
    clean_text = re.sub(r'[^\x20-\x7E\n]', '', clean_text) # removing weird characters (only keeping ASCII and newlines)
    clean_text = re.sub(r' +', ' ', clean_text) # If lines have multiple spaces collapsing them into single space
    return clean_text


def looks_like_paragraph(line):
    # Regex to detect if it looks like beginning
    if len(line) < 70:
        return False

    if line.isupper(): # Rejects all uppercase
        return False
    
    if not (re.search(r"[a-z]", line)): # Rejects if does not contain lowercase
        return False

    if not (re.search(r"[.,!?]", line)): # Rejects if does not contain punctuation
        return False
    
    return True


def print_first_n_lines(text, n=10):
    # For testing
    lines = text.splitlines()
    for line in lines[:n]:
        print(line)


def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_title(text):
    """
    Try to extract title from beginning of Gutenberg book.
    Usually appears near the top after header stripping.
    """
    lines = text.splitlines()
    for line in lines[:20]:
        if line.strip() and line.isupper() is False:
            if len(line.split()) <= 15:
                return line.strip()
    return "Unknown Title"


def fetch_gutenberg_license(book_id):
    rdf_url = f"https://www.gutenberg.org/ebooks/{book_id}.rdf"
    headers = {"User-Agent": "SotonLM-Test"}

    try:
        r = requests.get(rdf_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None, None

        root = ET.fromstring(r.content)

        # Namespaces used in Gutenberg RDF
        ns = {
            "dcterms": "http://purl.org/dc/terms/",
        }

        rights = root.find(".//dcterms:rights", ns)
        if rights is not None and rights.text:
            rights_text = rights.text.strip()

            if "public domain" in rights_text.lower():
                return "public_domain", rights_text
            else:
                return "other", rights_text

    except Exception:
        pass

    return None, None


def write_gutenberg_jsonl(book_id, text, out_path="gutenberg.jsonl"):
    # Only write if extracted text is of reasonable length (e.g. > 1000 chars)
    if text is None:
        print(f"Skipping {book_id} due to fetch error")
        return

    if len(text) < 1000:
        print(f"Skipping {book_id} due to short text length ({len(text)} chars)")
        return

    title = extract_title(text)
    timestamp = iso_now()
    license = fetch_gutenberg_license(book_id)
    title = extract_title(text)

    obj = {
    "id": f"web_gutenberg_{book_id}",
    "source": "web",
    "subsource": "gutenberg",
    "language": "en",
    "length_tokens": 123456,
    "quality_score": 1.0,
    "text": text,
    "timestamp": timestamp,
    "title": title,
    "url": f"https://www.gutenberg.org/ebooks/{book_id}",
    "license_type": license[0] if license[0] else "Unknown License Type",
    "license": license[1] if license[1] else "Unknown License",
    "robots_txt_content": "User-agent: * Disallow: /ebooks/search"
    }

    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # For testing
    book_ids = [80000, 1342, 1661, 3600, 84, 11, 2701, 1080, 1952, 120]
    for bid in book_ids:
        text = harvest_text(bid)
        write_gutenberg_jsonl(bid, text)

    # Real when downloading full dataset, just loop through all page nums (up to 77000+)
    #for bid in range(77000):
        #write_gutenberg_jsonl(bid, harvest_text(bid))
