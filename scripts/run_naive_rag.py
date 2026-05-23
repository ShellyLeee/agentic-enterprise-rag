"""Run Baseline A: naive retrieve-then-generate RAG."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.answer_generator import AnswerGenerator
from src.generation.llm_client import LLMClient
from src.retrieval.retriever import Retriever


def load_config(config_path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run the Naive RAG baseline.")
    parser.add_argument("--question", required=True, help="Question to answer.")
    parser.add_argument("--top_k", type=int, default=5, help="Number of chunks to retrieve.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Vector index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force deterministic mock LLM mode.")
    parser.add_argument("--output", help="Optional JSON output path.")
    return parser


def main() -> None:
    """Run retrieval and grounded answer generation."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    llm_config = config.get("llm", {})
    generation_config = config.get("generation", {})
    model_name = str(config.get("models", {}).get("embedding_model", "BAAI/bge-small-en-v1.5"))

    retriever = Retriever.load(Path(args.index_dir), embedding_model=model_name)
    retrieved = retriever.retrieve(args.question, top_k=args.top_k)

    llm_client = LLMClient(llm_config, mock=bool(args.mock or llm_config.get("mock", False)))
    generator = AnswerGenerator(
        llm_client,
        max_context_chunks=int(generation_config.get("max_context_chunks", args.top_k)),
    )
    answer = generator.generate(args.question, retrieved)
    payload = {
        "question": answer.question,
        "answer": answer.answer,
        "prediction": answer.answer,
        "llm": {
            "mode": answer.llm_mode,
            "model": answer.llm_model,
        },
        "citations": answer.citations,
        "retrieved_chunks": answer.retrieved_chunks,
    }

    print("\nQuestion")
    print(answer.question)
    print("\nAnswer")
    print(answer.answer)
    print("\nRetrieved Chunks")
    for index, chunk in enumerate(answer.retrieved_chunks, start=1):
        metadata = chunk.get("metadata", {})
        print(
            f"{index}. score={chunk.get('score')} "
            f"source={metadata.get('file_name')} "
            f"page={metadata.get('page_number')} "
            f"section={metadata.get('section_title')} "
            f"chunk_id={chunk.get('chunk_id')}"
        )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nSaved JSON output to {output_path}")


if __name__ == "__main__":
    main()
