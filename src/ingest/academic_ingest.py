from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def iter_raw_academic_source() -> Iterable[Dict[str, Any]]:
    """
    TODO: implement this generator to yield raw academic records.

    Each yielded dict should look like:
        {
          "id": "...",               # unique within this source
          "raw_text": "full text",   # or enough info for the cleaner
          "lang_hint": "en",
          "subsource": "sample|arxiv|...",
          "title": "...",            # optional
          "url": "...",              # optional
          "timestamp": "..."         # optional
        }

    For now, you can:
      - read from some local sample file
      - or just yield a few hardcoded dicts for testing.
    """
    # TODO: replace this placeholder with real ingestion logic
    example = {
        "id": "raw1",
        "raw_text": "Example academic text about machine learning and statistics.",
        "lang_hint": "en",
        "subsource": "sample",
        "title": "Sample academic doc",
        "url": "https://example.com/sample",
    }
    yield example


def run_ingest(output_path: str) -> None:
    """
    Run academic ingestion and write raw JSONL to the given path.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f_out:
        for rec in iter_raw_academic_source():
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
