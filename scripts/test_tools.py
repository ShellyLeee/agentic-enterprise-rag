"""Smoke-test the reusable tool layer for the future Agentic RAG workflow."""

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
from src.tools import AnswerTool, QueryRewriteTool, RefusalTool, RerankTool, RetrievalTool


def load_config(config_path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Test Agentic RAG tool wrappers.")
    parser.add_argument("--question", required=True, help="Question to answer.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Vector index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force mock LLM mode.")
    return parser


def print_section(title: str, payload: dict[str, Any]) -> None:
    """Pretty-print a structured tool output."""
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2))


def main() -> None:
    """Run every tool once and print structured outputs."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))

    embedding_model = str(config.get("models", {}).get("embedding_model", "BAAI/bge-small-en-v1.5"))
    retrieval_config = config.get("retrieval", {})
    reranker_config = config.get("reranker", {})
    llm_config = config.get("llm", {})
    generation_config = config.get("generation", {})

    llm_client = LLMClient(
        model=llm_config.get("model"),
        temperature=float(llm_config.get("temperature", 0.0)),
        mock=bool(args.mock or llm_config.get("mock", False)),
    )

    retrieval_tool = RetrievalTool(embedding_model=embedding_model)
    rerank_tool = RerankTool(
        model_name=str(reranker_config.get("model", "BAAI/bge-reranker-base")),
        backend=str(reranker_config.get("backend", "auto")),
        fallback=bool(reranker_config.get("fallback", True)),
    )
    rewrite_tool = QueryRewriteTool(llm_client)
    answer_tool = AnswerTool(
        AnswerGenerator(
            llm_client,
            max_context_chunks=int(generation_config.get("max_context_chunks", 5)),
        )
    )
    refusal_tool = RefusalTool()

    retrieval_output = retrieval_tool.run(
        query=args.question,
        top_k=int(retrieval_config.get("retrieve_k", 10)),
        index_dir=args.index_dir,
    )
    print_section("RetrievalTool", retrieval_output)

    rerank_output = rerank_tool.run(
        query=args.question,
        retrieved_chunks=retrieval_output["retrieved_chunks"],
        top_n=int(retrieval_config.get("rerank_top_n", 5)),
    )
    print_section("RerankTool", rerank_output)

    rewrite_output = rewrite_tool.run(
        original_query="days?",
        reason="Need a policy-specific query for employee vacation accrual.",
        failed_evidence_summary="The vague query did not mention vacation or accrual.",
    )
    print_section("QueryRewriteTool", rewrite_output)

    answer_output = answer_tool.run(
        question=args.question,
        evidence_chunks=rerank_output["reranked_chunks"],
    )
    print_section("AnswerTool", answer_output)

    best_scores = [
        float(chunk.get("rerank_score", chunk.get("score", 0.0)))
        for chunk in rerank_output["reranked_chunks"][:3]
    ]
    refusal_output = refusal_tool.run(
        question="What is the company's parental leave policy?",
        reason="No retrieved evidence discusses parental leave.",
        best_scores=best_scores,
    )
    print_section("RefusalTool", refusal_output)


if __name__ == "__main__":
    main()

