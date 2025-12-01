from __future__ import annotations

import argparse
from pathlib import Path

from src.clean.web_clean import run_clean


DEFAULT_INPUT = "data/raw/web/sample_raw.jsonl"
DEFAULT_OUTPUT = "data/clean/web/sample_clean.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the web cleaning pipeline on a single raw JSONL file."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT,
        help=f"Path to raw web JSONL (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Path to write clean JSONL (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    run_clean(str(input_path), str(output_path))
    print(f"Cleaned web data written to: {output_path}")


if __name__ == "__main__":
    main()
