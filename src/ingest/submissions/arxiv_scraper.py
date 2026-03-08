"""
Gutenberg Text Harvester

Fetches a small number of Project Gutenberg books, (Just for testing as stated in instruction but can just loop through all page nums to do all)
removes license/header/footer text,

"""

import re
import random
import json
import hashlib
import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import os

import requests
from bs4 import BeautifulSoup
import fitz
import arxiv


BASE_URL = "https://arxiv.org/pdf/"
BASE_URL_HTML = "https://arxiv.org/abs/"
BASE_PAGES_TO_SCRAPE = "https://export.arxiv.org/api/query"


def get_paper_number_from_url(url):
    # Extract paper number from URL
    allSoup = BeautifulSoup(requests.get(url).content, "html.parser")

    # Entry format is a tuple of (id, title, timestamp)
    allEntrys = []

    # For every entry
    entrys = allSoup.find_all("entry")
    for entry in entrys:
        try:
            # Getting id
            id = entry.find("id")
            try:
                if id.text.startswith("http://arxiv.org/abs/"):
                    parts = id.text.split("/")
                    paper_num = (parts[-1])
                else:
                    continue
            except Exception as e:
                print(f"Error extracting paper number from {url}: {e}")
                continue

            # Getting Title
            try:
                title = entry.find("title")
                title = title.text
            except Exception as e:
                print(f"Error finding paper title from {url}: {e}")
                title = "N/A"
            
            # Getting Timestamp
            try:
                time = entry.find("published")
                time = time.text
            except Exception as e:
                print(f"Error finding timestamp from {url}: {e}")
                time = "N/A"

            allEntrys.append((paper_num, title, time))
        except Exception as e:
            continue
    return allEntrys


def harvest_text(paper_num):
    # Getting actual text
    target_url = f"{BASE_URL}{paper_num}.pdf"

    headers = {
        "User-Agent": "SotonLM-Test"
    }

    try:
        r = requests.get(target_url, headers=headers, timeout=15)

        if r.status_code == 200:
            return r
        else:
            print(f"Failed {paper_num} (status {r.status_code})")

    except Exception as e:
        print(f"Error fetching {paper_num}: {e}")
        

def convert_pdf_to_raw_text(pdf):
    doc = fitz.open(stream=pdf.content, filetype="pdf")

    rawtext = ""

    for page in doc:
        rawtext += page.get_text()

    return rawtext


def get_final_text(url):
    allEntrys = get_paper_number_from_url(url)

    # Looping through every entry, harvesting text saving to json
    for entry in allEntrys:
        # Be polite to not get blocked (when harvesting)
        time.sleep(random.uniform(2, 3))

        id, title, timestamp = entry

        pdf = harvest_text(id)
        text = convert_pdf_to_raw_text(pdf)
        cleanedtext = cleantext(text)

        write_arxiv_jsonl(cleanedtext, title, timestamp, id)


def cleantext(text):
    cleaned = ""
    for line in text.split("\n"):
        if remove_junk_lines(line):
            continue
        
        cleaned += line + "\n"

    return final_clean(cleaned)


def remove_junk_lines(line):
    # Removing tables (usually consists of) Lots of nums, short tokens seperated by spaces, very little puntuation

    line = line.strip()
    length = len(line)
    ints = 0
    for char in line:
        ints += 1 if char.isdigit() else 0 

    # Keep blank lines
    if not line:
        return False

    if length < 3:
        return True

    # 2. Few normal words
    words = re.findall(r"[a-zA-Z]{2,}", line)
    if len(words) == 0:
        return True

    # 3. Too many symbols
    symbols = re.findall(r"[^a-zA-Z0-9\s]", line)
    if len(symbols) / max(len(line),1) > 0.5:
        return True

    # If amount of nums in line above 50%
    if ints / max(length, 1) > 0.5:
        return True

    return False


def is_mixed_junk(line):
    """
    Return True if line is short and contains mostly symbols or <5 normal words
    """
    line = line.strip()
    if not line:
        return True  # blank lines are OK to keep

    words = re.findall(r"[a-zA-Z]{2,}", line)
    word_count = len(words)
    symbols = re.findall(r"[^a-zA-Z0-9\s]", line)
    symbol_ratio = len(symbols) / max(len(line),1)

    # line is mostly junk if too few normal words OR too many symbols
    if word_count <= 2 or symbol_ratio > 0.3:
        return True
    return False


def block_of_junk(raw_text, min_streak=3):
    lines = raw_text.splitlines()
    cleaned = []
    streak = []

    for line in lines:
        if is_mixed_junk(line):
            streak.append(line)
        else:
            if len(streak) >= min_streak:
                # discard streak
                streak = []
            else:
                # keep short streaks
                cleaned.extend(streak)
                streak = []
            cleaned.append(line)

    # handle trailing streak at end
    if len(streak) < min_streak:
        cleaned.extend(streak)

    return "\n".join(cleaned)



def final_clean(raw_text):
    """
    Removing trailing spaces
    Collapsing multiple blank lines to a single blank line
    Keeping only ASCII printable characters
    """
    clean_text = block_of_junk(raw_text)
    clean_text = "\n".join(line.strip() for line in clean_text.splitlines())
    clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)  # replace multiple empty lines with just two newlines
    clean_text = re.sub(r'[^\x20-\x7E\n]', '', clean_text) # removing weird characters (only keeping ASCII and newlines)
    clean_text = re.sub(r' +', ' ', clean_text) # If lines have multiple spaces collapsing them into single space
    return clean_text



def print_first_n_lines(text, n=10):
    # For testing
    lines = text.splitlines()
    for line in lines[:n]:
        print(line)



def fetch_arxiv_license(arxiv_id):
    """
    Fetches license information from the RDF metadata of the book.
    """
    try:
        r = requests.get(BASE_URL_HTML + arxiv_id)
        soup = BeautifulSoup(r.text, "html.parser")
        license_div = soup.find('div', class_='abs-license')
        if license_div:
            link = license_div.find('a')
            if link and link.has_attr('href'):
                return link['href']
            else:
                return license_div
    except Exception as e:
        print("Error getting license")
        return "Unavailable"


def count_tokens(text: str) -> int:
    # Split on whitespace
    return len(text.split())

def basic_quality(text: str, tokens: int) -> float:
    # Basic heuristic: longer texts with more punctuation are likely higher quality
    length_score = min(1.0, tokens / 100000)  # Cap at 100k tokens for scoring
    punctuation_score = min(1.0, sum(text.count(p) for p in ".,!?;:") / 1000)  # Cap at 1000 punctuation marks
    return (length_score + punctuation_score) / 2


def write_arxiv_jsonl(text, title, timestamp, id, out_path="./data_temp/arxiv.jsonl"):
    # Only write if extracted text is of reasonable length (e.g. > 1000 chars) and not None (fetch error)

    license = fetch_arxiv_license(id)
    license_type = license.split()[0] if license and len(license.split()) > 0 else "Unknown License Type"
    tokens = count_tokens(text)
    quality_score = basic_quality(text, tokens)

    obj = {
    "id": id,
    "source": "web",
    "subsource": "arxiv",
    "language": "en",
    "length_tokens": tokens,
    "quality_score": quality_score,
    "text": text,
    "timestamp": timestamp,
    "title": title,
    "url": f"{BASE_URL}{id}.pdf",
    "license_type": license_type,
    "license": license,
    "robots_txt_content": "User-agent: * Disallow: /"
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # Loop through and cycle through all papers

    get_final_text(BASE_PAGES_TO_SCRAPE)

