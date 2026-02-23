"""
Gutenberg Text Harvester

Fetches a small number of Project Gutenberg books, (Just for testing as stated in instruction but can just loop through all page nums to do all)
removes license/header/footer text,

"""

import requests
import re


def harvest_text(book_id):
    # Taking book_id and then scraping txt off that page
    # Already provided with .txt files no need for HTML parser
    target_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"

    # To be polite to website
    headers = {"User-Agent": "SotonLM-Test"}

    r = requests.get(target_url, headers=headers)
    if r.status_code == 200:
        rawtext = r.text
        print_first_n_lines(strip_gutenberg_headers(rawtext), 500) # Change this later to just save as JSON?
        

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


def skip_to_first_paragraph(raw_text):
    """
    Most books include contents page or other jargon like authors address ect, so trying to skip that
    """


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


if __name__ == "__main__":
    # For testing
    book_ids = [100, 1342, 1661]
    for bid in book_ids:
        harvest_text(bid)

    # Around 77000 books in library currently
    #for bid in range(77000):
        #harvest_text(bid)

