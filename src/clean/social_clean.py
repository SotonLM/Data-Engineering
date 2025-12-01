from __future__ import annotations

from typing import Optional, Dict, Any

from src.shared.schema import make_clean_record, validate_clean_record
from src.shared.io import read_jsonl, write_jsonl, write_jsonl_record

MIN_TOKENS = 5
MAX_TOKENS = 400  # social posts are shorter


def clean_social_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Convert a raw social record into a clean record, or return None to drop it.

    Expected raw schema (for now, for sample files):
        {
          "id": "raw1",
          "text": "full post text",
          "lang_hint": "en",
          "subsource": "reddit|twitter|...",
          "timestamp": "...",   # optional
          "url": "...",         # optional
        }
    """

    # TODO: normalise the raw social text
    # - resolve or remove mentions/handles
    # - strip excessive emojis / noise if needed
    # - normalise whitespace
    # - maybe expand common abbreviations, etc.
    text = (raw.get("text") or "").strip()

    if not text:
        return None

    tokens = text.split()
    token_count = len(tokens)

    # Standard token length filtering
    if token_count < MIN_TOKENS or token_count > MAX_TOKENS:
        return None

    clean = make_clean_record(
        source="social",
        subsource=str(raw.get("subsource", "sample")),
        raw_id=str(raw.get("id", "")),
        text=text,
        lang_hint=str(raw.get("lang_hint", "en")),
        url=raw.get("url"),
        title=None,
        timestamp=raw.get("timestamp"),
        quality_score=1.0,  # TODO later
    )

    if not validate_clean_record(clean):
        return None

    return clean


def run_clean(input_path: str, output_path: str) -> None:
    """
    Run the social cleaning pipeline on a single input JSONL file and
    write a clean JSONL output file.
    """
    with write_jsonl(output_path) as f_out:
        for raw in read_jsonl(input_path):
            clean = clean_social_record(raw)
            if clean is None:
                continue
            write_jsonl_record(f_out, clean)
