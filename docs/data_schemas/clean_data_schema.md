# Clean Data Schema (v1)

WARNING : THIS SCHEMA IS INCOMPLETE. 

At the current stage of development, we arent concerning the cleaning process of data.
We will work on this when the time is right.

## Required fields

These **must** exist on every clean record.

| Field          | Type    | Description                                                    |
|----------------|---------|----------------------------------------------------------------|
| `id`           | string  | Globally unique ID, usually `"{source}_{raw_id}"`.            |
| `division`       | string  | High-level domain: `academic`, `web`, `social`, or `other`.   |
| `source`    | string  | More specific origin, e.g. `arxiv`, `wikipedia`, `bluesky`.    |

| `lang`         | string  | ISO language code, e.g. `en`.                                 |
| `length_tokens`| int     | Number of whitespace-split tokens in `text`.                  |
| `quality_score`| float   | Heuristic in `[0.0, 1.0]` (1.0 for now, refined later).       |
| `text`         | string  | Cleaned document text, ready for tokenisation.                |

Rules:

- `source` **must** be one of: `academic`, `web`, `social`, `other`.
- `length_tokens > 0`.
- `quality_score` is a float; `1.0` is “keep”, lower values are filtered downstream.
- `text` must be non-empty, no raw HTML, no obvious garbage.

---

## Optional fields

These may be `null` or omitted if unknown.

| Field       | Type     | Description                         |
|-------------|----------|-------------------------------------|
| `timestamp` | string   | ISO8601 timestamp for document.     |
| `title`     | string   | Document title / headline.          |
| `url`       | string   | Source URL if applicable.           |

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
