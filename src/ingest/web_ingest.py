from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def iter_raw_web_source() -> Iterable[Dict[str, Any]]:
    """
    TODO: implement this generator to yield raw web records.

    Each yielded dict should look like:
        {
          "id": "...",
          "raw_text": "full page text",  # or "html": "<html>...</html>" if you prefer
          "lang_hint": "en",
          "subsource": "sample|wikipedia|news|...",
          "title": "...",                # optional
          "url": "...",                  # optional
          "timestamp": "..."             # optional
        }
    """
    # TODO: replace this placeholder with real ingestion logic
    example = {
        "id": "raw_web_1",
        "raw_text": "Example web page text.",
        "lang_hint": "en",
        "subsource": "sample",
        "title": "Sample web page",
        "url": "https://example.com/web1",
    }
    yield example


def run_ingest(output_path: str) -> None:
    """
    Run web ingestion and write raw JSONL to the given path.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f_out:
        for rec in iter_raw_web_source():
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
