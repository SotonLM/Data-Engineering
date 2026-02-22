# Clean Data Schema (v1)

This document defines the **canonical schema** for all *clean* documents
stored under `data/clean/**` and used for sharding / mixtures / training.

Each line in a clean JSONL file is **one document** (e.g. one webpage, one paper,
one social post), represented as a single JSON object with the fields below.

---

## Required fields


These **must** exist on every stored raw data.

| Field          | Type    | Description                                                    |
|----------------|---------|----------------------------------------------------------------|
| `id`           | string  | Globally unique ID. This will be "{hash of fetched_url}_{timestamp}"|
| 'run_id'       | string  | ID generated when running the script on this json object. This will be in the form : "" |
| `timestamp`    | string  | ISO8601 timestamp for document.                               |
| `source`       | string  | More specific origin, e.g. `arxiv`, `wikipedia`, `bluesky`.   |
| 'content_type' | string  | "Social", "Academic", "Web", etc. Rough type of content assumed based on the source platform. |
| `reqeusted_url`| string  | URL used in the fetch function.                               |
| 'fetched_url'  | string  | URL the fetch request actually reached.                       |
| 'status_code'  | int     | Result of fetch request. E.g. "404" is not found and "200" is OK. |
| `length`       | int     | Number of tokens in the raw content.                          |
| `raw_content`  | string  | Cleaned document text, ready for tokenisation.                |
|'content_format'| string | Format of the raw content e.g. html, plain text, etc           |
| 'content_hash' | string  | SHA_256 hashing of the raw content                            |


Rules:
- As stated above, hashing should be done using SHA_256. 
    To clarify, the "hash of fetched url" for the "id" field will also be hashed in SHA_256.


---

## Nullable fields

These may be `null` or omitted if unknown. 

NOTE: in terms of legal data, if both the licensing and robots.txt content are unknown, DO NOT INGEST that data.

| Field       | Type     | Description                         |
|-------------|----------|-------------------------------------|
| `title`     | string   | Document title / headline.          |
| 'license_type'| string | 'MIT' and 'Apache 2.0' are common examples of open source licenses|
| 'license'   | string   | Main legal metadata.                |
| 'robots_txt_content' | string | robots.txt is a file on a webpage which kindly asks you to handle data from the webpage under a certain bunch of rules. Good to see if we are using the data in an ethical manner|
| 'language' | string | Just to make sure its in english.      |

---

## Example clean records

### Academic example

```json
{
  "id": "academic_raw1",
  "source": "academic",
  "subsource": "sample",
  "lang": "en",
  "length_tokens": 1200,
  "quality_score": 1.0,
  "text": "Full cleaned academic text...",
  "timestamp": "2024-11-01T12:00:00Z",
  "title": "Sample academic doc",
  "url": "https://example.com/sample1"
}

### Web Example

```json
{
  "id": "web_42",
  "source": "web",
  "subsource": "wikipedia",
  "lang": "en",
  "length_tokens": 2300,
  "quality_score": 0.95,
  "text": "Full cleaned article text...",
  "title": "Example Article",
  "url": "https://en.wikipedia.org/wiki/Example"
}

### Social Example

```json
{
  "id": "social_abc123",
  "source": "social",
  "subsource": "reddit",
  "lang": "en",
  "length_tokens": 60,
  "quality_score": 1.0,
  "text": "Post or comment text...",
  "timestamp": "2024-10-02T09:30:00Z",
  "url": "https://reddit.com/r/.../comments/..."
}



- At the current progress, ok good we got the wikipedia ingestion script going and we managed to get 90+ GB of data.
- We have a sharding script
