from __future__ import annotations

from typing import Optional, Dict, Any

from src.shared.schema import make_clean_record, validate_clean_record
from src.shared.io import read_jsonl, write_jsonl, write_jsonl_record


# Token limits for academic text
MIN_TOKENS = 10
MAX_TOKENS = 8000


def clean_academic_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert a raw academic record into a clean record, or return None to drop it.

    Expected raw schema for now:
        {
          "id": "raw1",
          "raw_text": "full academic text...",
          "lang_hint": "en",
          "subsource": "sample",
          "title": "...",      # optional
          "url": "...",        # optional
          "timestamp": "..."   # optional
        }
    """

    # ---------------------------
    # TODO: domain-specific cleaning goes here
    # ---------------------------
    # For now we assume `raw_text` is already extracted.
    text = (raw.get("raw_text") or "").strip()
    # ---------------------------

    if not text:
        return None

    tokens = text.split()
    token_count = len(tokens)

    # Standard length filtering (do not change logic)
    if token_count < MIN_TOKENS or token_count > MAX_TOKENS:
        return None

    # Build clean record
    clean = make_clean_record(
        source="academic",
        subsource=str(raw.get("subsource", "sample")),
        raw_id=str(raw.get("id", "")),
        text=text,
        lang_hint=str(raw.get("lang_hint", "en")),
        url=raw.get("url"),
        title=raw.get("title"),
        timestamp=raw.get("timestamp"),
        quality_score=1.0,  # placeholder — upgraded later
    )

    # Validate clean record
    if not validate_clean_record(clean):
        return None

    return clean


def run_clean(input_path: str, output_path: str) -> None:
    """
    Read raw JSONL -> clean -> write clean JSONL.
    """

    with write_jsonl(output_path) as f_out:
        for raw in read_jsonl(input_path):
            clean = clean_academic_record(raw)
            if clean is None:
                continue
            write_jsonl_record(f_out, clean)
