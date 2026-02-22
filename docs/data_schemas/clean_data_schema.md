# Clean Data Schema (v1.1)

This document defines the **canonical schema** for all *clean* documents stored under `data/clean/**` and used for sharding / mixtures / training.

Each line in a clean JSONL file is **one document** (e.g., one webpage, one paper, one social post), represented as a single JSON object with the fields below.

---


## Prerequisites


- Upon cleaning, scripts should check if the raw data allows use of it. For example, it should have an open source license, and/or a robots.txt which allows data scraping in our context of training an LLM.
- For cleaned data, there should be scripts to trim data which yield a low quality score. My recommended threshold would be 0.7+, but you guys can decide on that as well.
- By the end of this, we expect 100GB of CLEAN, HIGH QUALITY data. This is why terabytes of raw data may be necessary.

## Non-null fields
These **must** exist on every stored clean document.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Globally unique ID for the clean data. Format: `{source}_{content_hash[:16]}` (truncated hash for readability) |
| `raw_id` | string | ID of the raw data used for cleaning.|
| `run_id` | string | ID generated when running the cleaning script|
| `timestamp` | string | ISO8601 timestamp when the document was fetched/processed |
| `source` | string | Broad source category, e.g. `academic`, `web`, `social`, `news` |
| `subsource` | string | Specific origin platform, e.g. `arxiv`, `wikipedia`, `reddit`, `bluesky` |
| `content_type` | string | Type of content: `article`, `paper`, `post`, `comment`, `discussion` |
| `length` | int | Number of characters in cleaned content |
| `length_tokens` | int | Estimated number of tokens |
| `word_count` | int | Number of words in cleaned text |
| `sentence_count` | int | Approximate number of sentences |
| `quality_score` | float | Cleaned Quality Score. One of the objectives is to preserve clean data with high quality score, and delete those with low scores.|
| `text` | string | Cleaned document text, ready for tokenisation |
| `content_hash` | string | SHA-256 hash of the cleaned text content |


---

## Nullable fields

These may be `null` or omitted if unknown.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title or headline |
| `author` | string | Author name(s) if available |
| `published_date` | string | Original publication date (ISO8601) if different from fetch date |
| `language` | string | ISO 639-1 language code (e.g., `en`, `es`, `fr`) |
| `license_type`| string | 'MIT' and 'Apache 2.0' are common examples of open source licenses|
| `license`   | string   | Main legal metadata.                |
| `robots_txt` | string | Content of robots.txt if relevant for ethical compliance |
| `robots_allowed` | boolean | Whether robots.txt allows fetching/using this content |
| `file_type` | string | Original file type if applicable (e.g., `pdf`, `html`, `txt`) |
| `has_code` | boolean | Whether the document contains code blocks |
| `has_tables` | boolean | Whether the document contains tables |
| `has_images` | boolean | Whether the document references images |
| `metadata` | object | Any other metadata or notes regarding this object. |
| `processing_version` | string | Version of cleaning pipeline used |
| `processing_steps` | array[string] | List of cleaning steps applied. e.g. "remove table formattings", "remove indexing" etc. Each part of the cleaning script should log a different step of cleaning depending on what they do. |
