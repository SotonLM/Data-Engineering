from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


# ---- Clean record definition ----

REQUIRED_FIELDS = [
    "id",
    "source",
    "subsource",
    "lang",
    "length_tokens",
    "quality_score",
    "text",
]

OPTIONAL_FIELDS = [
    "timestamp",
    "title",
    "url",
]


@dataclass
class CleanRecord:
    id: str
    source: str              # e.g. "academic", "web", "social"
    subsource: str           # e.g. "arxiv", "wikipedia", "reddit"
    lang: str                # ISO language code, e.g. "en"
    length_tokens: int
    quality_score: float     # 0.0–1.0 heuristic; can be 1.0 for now
    text: str

    # Optional metadata
    timestamp: Optional[str] = None  # ISO8601 or None
    title: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict suitable for JSON serialisation."""
        return asdict(self)


def make_clean_record(
    *,
    source: str,
    subsource: str,
    raw_id: str,
    text: str,
    lang_hint: str = "en",
    url: Optional[str] = None,
    title: Optional[str] = None,
    timestamp: Optional[str] = None,
    quality_score: float = 1.0,
) -> Dict[str, Any]:
    """
    Convenience constructor used by cleaners.
    Handles ID generation and basic length/token logic.
    """
    text = text.strip()
    tokens = text.split()
    rec = CleanRecord(
        id=f"{source}_{raw_id}",
        source=source,
        subsource=subsource,
        lang=lang_hint,
        length_tokens=len(tokens),
        quality_score=float(quality_score),
        text=text,
        timestamp=timestamp,
        title=title,
        url=url,
    )
    return rec.to_dict()


def validate_clean_record(rec: Dict[str, Any]) -> bool:
    """
    Quick sanity check that a record conforms to the clean schema.
    This is deliberately cheap, not a full validator.
    """
    # Required keys present
    if not all(k in rec for k in REQUIRED_FIELDS):
        return False

    if not isinstance(rec["id"], str) or not rec["id"]:
        return False
    if rec["source"] not in {"academic", "web", "social", "other"}:
        return False
    if not isinstance(rec["subsource"], str):
        return False
    if not isinstance(rec["lang"], str) or len(rec["lang"]) == 0:
        return False
    if not isinstance(rec["length_tokens"], int) or rec["length_tokens"] <= 0:
        return False
    if not isinstance(rec["quality_score"], (int, float)):
        return False
    if not isinstance(rec["text"], str) or not rec["text"].strip():
        return False

    return True
