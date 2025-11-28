from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def iter_raw_social_source() -> Iterable[Dict[str, Any]]:
    """
    TODO: implement this generator to yield raw social records.

    Each yielded dict should look like:
        {
          "id": "...",
          "text": "post/comment text",
          "lang_hint": "en",
          "subsource": "reddit|twitter|discord|...",
          "timestamp": "...",     # optional
          "url": "..."            # optional
        }
    """
    # TODO: replace this placeholder with real ingestion logic
    example = {
        "id": "raw_social_1",
        "text": "Example social media post.",
        "lang_hint": "en",
        "subsource": "sample",
        "timestamp": None,
        "url": None,
    }
    yield example


def run_ingest(output_path: str) -> None:
    """
    Run social ingestion and write raw JSONL to the given path.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f_out:
        for rec in iter_raw_social_source():
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
