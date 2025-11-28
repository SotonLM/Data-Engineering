from __future__ import annotations

import json
from pathlib import Path
from typing import List


def build_shards(
    input_paths: List[str],
    output_dir: str,
    docs_per_shard: int = 10_000,
) -> None:
    """
    TODO: later – move to token-based sharding and zstd compression.
    For now: naive doc-count-based sharding.

    - input_paths: list of clean JSONL files for a single domain
    - output_dir: directory to write shard JSONL files into
    """
    out_base = Path(output_dir)
    out_base.mkdir(parents=True, exist_ok=True)

    shard_idx = 0
    doc_in_shard = 0
    f_out = None

    def _open_new_shard():
        nonlocal shard_idx, doc_in_shard, f_out
        if f_out is not None:
            f_out.close()
        shard_path = out_base / f"shard_{shard_idx:06d}.jsonl"
        f_out = shard_path.open("w", encoding="utf-8")
        shard_idx += 1
        doc_in_shard = 0

    _open_new_shard()

    try:
        for input_path in input_paths:
            in_path = Path(input_path)
            with in_path.open("r", encoding="utf-8") as f_in:
                for line in f_in:
                    if not line.strip():
                        continue
                    if doc_in_shard >= docs_per_shard:
                        _open_new_shard()
                    f_out.write(line)
                    doc_in_shard += 1
    finally:
        if f_out is not None:
            f_out.close()
