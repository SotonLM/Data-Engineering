from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Iterator, Dict, Any, TextIO


# ---- Plain JSONL helpers (no compression yet) ----


def read_jsonl(path: str) -> Iterator[Dict[str, Any]]:
    """Stream JSON objects from a .jsonl file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


@contextmanager
def write_jsonl(path: str) -> Iterator[TextIO]:
    """Context manager that yields a file handle for writing JSONL."""
    f = open(path, "w", encoding="utf-8")
    try:
        yield f
    finally:
        f.close()


def write_jsonl_record(f: TextIO, rec: Dict[str, Any]) -> None:
    """Write a single record as one JSONL line."""
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
