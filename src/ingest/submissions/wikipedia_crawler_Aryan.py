import urllib.request
import urllib.parse
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

START_URL = "https://en.wikipedia.org/wiki/Web_scraping"
DOMAIN = "wikipedia.org"
MAX_PAGES = 5


class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text_chunks = []
        self.in_paragraph = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (attr, value) in attrs:
                if attr == "href":
                    self.links.append(value)
        if tag == "p":
            self.in_paragraph = True

    def handle_endtag(self, tag):
        if tag == "p":
            self.in_paragraph = False

    def handle_data(self, data):
        if self.in_paragraph:
            cleaned = data.strip()
            if cleaned:
                self.text_chunks.append(cleaned)


def fetch(url):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode("utf-8", errors="ignore")
            #print(result)
            return result
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def extract(url, html):
    parser = SimpleHTMLParser()
    parser.feed(html)

    full_links = [urljoin(url, link) for link in parser.links]

    return parser.text_chunks, full_links


def crawl(start_url):
    visited = set()
    to_visit = [start_url]
    results = []

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print(f"Crawling: {url}")
        html = fetch(url)
        if not html:
            continue

        visited.add(url)
        text, links = extract(url, html)

        results.append({
            "url": url,
            "sample_text": text[:100], #change this number to store more/less words
        })

        # Add new internal links
        for link in links:
            if DOMAIN in urlparse(link).netloc and link not in visited:
                to_visit.append(link)

    return results


# Run the crawler
data = crawl(START_URL)

# Print results
for item in data: #could add write to file here if wanted
    print("\n--- Page ---")
    print("URL:", item["url"])
    print("Sample text:", item["sample_text"])