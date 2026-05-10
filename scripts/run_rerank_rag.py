"""Run Baseline B: retrieve, rerank, then generate."""

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
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever


def load_config(config_path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run the RAG + reranker baseline.")
    parser.add_argument("--question", required=True, help="Question to answer.")
    parser.add_argument("--retrieve_k", type=int, help="Number of chunks to retrieve before reranking.")
    parser.add_argument("--rerank_top_n", type=int, help="Number of reranked chunks to answer from.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Vector index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force deterministic mock LLM mode.")
    parser.add_argument("--output", help="Optional JSON output path.")
    return parser


def main() -> None:
    """Run retrieve, rerank, and grounded answer generation."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))

    retrieval_config = config.get("retrieval", {})
    reranker_config = config.get("reranker", {})
    llm_config = config.get("llm", {})
    generation_config = config.get("generation", {})

    retrieve_k = int(args.retrieve_k or retrieval_config.get("retrieve_k", 10))
    rerank_top_n = int(args.rerank_top_n or retrieval_config.get("rerank_top_n", 5))
    embedding_model = str(config.get("models", {}).get("embedding_model", "BAAI/bge-small-en-v1.5"))

    retriever = Retriever.load(Path(args.index_dir), embedding_model=embedding_model)
    retrieved = retriever.retrieve(args.question, top_k=retrieve_k)

    reranker = Reranker(
        model_name=str(reranker_config.get("model", "BAAI/bge-reranker-base")),
        backend=str(reranker_config.get("backend", "auto")),
        fallback=bool(reranker_config.get("fallback", True)),
    )
    reranked = reranker.rerank(args.question, retrieved, top_n=rerank_top_n)

    llm_client = LLMClient(
        model=llm_config.get("model"),
        temperature=float(llm_config.get("temperature", 0.0)),
        mock=bool(args.mock or llm_config.get("mock", False)),
    )
    generator = AnswerGenerator(
        llm_client,
        max_context_chunks=int(generation_config.get("max_context_chunks", rerank_top_n)),
    )
    answer = generator.generate(args.question, reranked)

    payload = {
        "question": answer.question,
        "answer": answer.answer,
        "llm": {"mode": answer.llm_mode, "model": answer.llm_model},
        "reranker": {"backend": reranker.backend_used, "model": reranker.model_name},
        "citations": answer.citations,
        "reranked_chunks": answer.retrieved_chunks,
    }

    print("\nQuestion")
    print(answer.question)
    print("\nAnswer")
    print(answer.answer)
    print(f"\nReranker Backend\n{reranker.backend_used}")
    print("\nReranked Chunks")
    for index, chunk in enumerate(answer.retrieved_chunks, start=1):
        metadata = chunk.get("metadata", {})
        print(
            f"{index}. retrieval_score={chunk.get('retrieval_score')} "
            f"rerank_score={chunk.get('rerank_score')} "
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

