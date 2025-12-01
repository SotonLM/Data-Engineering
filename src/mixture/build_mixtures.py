from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def build_mixture(
    config: Dict[str, List[str]],
    output_path: str,
) -> None:
    """
    Very naive mixture builder.

    config example:
        {
          "academic": ["data/shard/academic/shard_000000.jsonl"],
          "web": ["data/shard/web/shard_000000.jsonl"],
          "social": ["data/shard/social/shard_000000.jsonl"]
        }

    TODO: later – add weighting, sampling, randomisation.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f_out:
        for domain, paths in config.items():
            for p in paths:
                in_path = Path(p)
                with in_path.open("r", encoding="utf-8") as f_in:
                    for line in f_in:
                        if not line.strip():
                            continue
                        # Optionally tag the domain here if not already in record
                        f_out.write(line)
