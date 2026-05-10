"""Smoke-test retrieval against a persisted vector index."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.retriever import Retriever


def load_embedding_model(config_path: Path) -> str:
    """Read the embedding model name from YAML config."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return str(config.get("models", {}).get("embedding_model", "BAAI/bge-small-en-v1.5"))


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Retrieve chunks from a persisted vector index.")
    parser.add_argument("--query", required=True, help="Question or search query.")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Index directory.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    return parser


def main() -> None:
    """Run a retrieval smoke test."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    model_name = load_embedding_model(Path(args.config))
    retriever = Retriever.load(Path(args.index_dir), embedding_model=model_name)
    results = retriever.retrieve(args.query, top_k=args.top_k)

    print(f"query={args.query}")
    print(f"backend={retriever.backend_info['backend']}")
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        section = metadata.get("section_title") or "unknown section"
        file_name = metadata.get("file_name") or "unknown file"
        print(f"\n{rank}. score={result['score']} chunk_id={result['chunk_id']}")
        print(f"   source={file_name} page={metadata.get('page_number')} section={section}")
        print(f"   text={result['text'][:300].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()

