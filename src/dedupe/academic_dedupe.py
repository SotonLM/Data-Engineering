from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Set


def _hash_text(text: str) -> str:
    """Simple hash helper for exact-duplicate detection."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def dedupe_academic(input_path: str, output_path: str) -> None:
    """
    TODO: later – extend this to near-duplicate (MinHash/SimHash).
    For now, exact duplicate removal based on `text` field.
    """
    in_path = Path(input_path)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    seen_hashes: Set[str] = set()

    with in_path.open("r", encoding="utf-8") as f_in, out_path.open(
        "w", encoding="utf-8"
    ) as f_out:
        for line in f_in:
            if not line.strip():
                continue
            rec: Dict[str, Any] = json.loads(line)
            text = rec.get("text", "")
            if not text:
                continue

            h = _hash_text(text)
            if h in seen_hashes:
                # duplicate, skip
                continue
            seen_hashes.add(h)
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
