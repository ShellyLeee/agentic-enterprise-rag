"""Build a persisted vector index from chunk JSONL."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.vector_index import build_vector_index


def load_embedding_model(config_path: Path) -> str:
    """Read the embedding model name from YAML config."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return str(config.get("models", {}).get("embedding_model", "BAAI/bge-small-en-v1.5"))


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Build a vector index from processed chunks.")
    parser.add_argument("--chunks", default="data/processed/chunks.jsonl", help="Input chunks JSONL.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Output index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    return parser


def main() -> None:
    """Run vector index construction."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    model_name = load_embedding_model(Path(args.config))
    info = build_vector_index(
        chunks_path=Path(args.chunks),
        index_dir=Path(args.index_dir),
        embedding_model=model_name,
    )
    print(f"embedding_model={info.embedding_model}")
    print(f"embedding_backend={info.embedding_backend}")
    print(f"chunks_indexed={info.chunk_count}")
    print(f"backend={info.backend}")
    print(f"index_dir={info.index_dir}")


if __name__ == "__main__":
    main()

