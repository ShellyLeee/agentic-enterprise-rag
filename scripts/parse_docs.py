"""Parse raw enterprise documents into normalized chunk JSONL."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingest.pipeline import run_ingestion


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Parse documents into data/processed/chunks.jsonl.")
    parser.add_argument("--input_dir", default="data/raw_docs", help="Directory containing raw docs.")
    parser.add_argument("--output", default="data/processed/chunks.jsonl", help="Output JSONL path.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    return parser


def main() -> None:
    """Run the parse-docs CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    stats = run_ingestion(
        input_dir=Path(args.input_dir),
        output_path=Path(args.output),
        config_path=Path(args.config),
    )
    print(f"documents={stats.documents} pages={stats.pages} chunks={stats.chunks}")
    print(f"output={stats.output_path}")


if __name__ == "__main__":
    main()
