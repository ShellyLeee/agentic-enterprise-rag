"""Run the explicit evidence-aware Agentic RAG workflow."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import (
    AgentPlanner,
    AgentTools,
    AgentTraceLogger,
    EvidencePolicy,
    EvidencePolicyConfig,
    RagAgentExecutor,
)
from src.generation.answer_generator import AnswerGenerator
from src.generation.llm_client import LLMClient
from src.tools import AnswerTool, QueryRewriteTool, RefusalTool, RerankTool, RetrievalTool


def load_config(config_path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run the evidence-aware Agentic RAG workflow.")
    parser.add_argument("--question", required=True, help="Question to answer.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Vector index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force deterministic mock LLM mode.")
    parser.add_argument("--save_trace", help="Optional JSON trace path.")
    parser.add_argument(
        "--agent_policy",
        choices=["conservative", "balanced", "aggressive"],
        help="Named evidence policy preset.",
    )
    return parser


def main() -> None:
    """Run the agentic workflow."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))

    models = config.get("models", {})
    retrieval_config = config.get("retrieval", {})
    reranker_config = config.get("reranker", {})
    generation_config = config.get("generation", {})
    llm_config = config.get("llm", {})
    agent_config = config.get("agent", {})
    policy_name = args.agent_policy or agent_config.get("default_policy", "balanced")
    policy_presets = agent_config.get("policy_presets", {})
    selected_policy = policy_presets.get(policy_name)
    if selected_policy is None:
        raise ValueError(f"Unknown agent policy preset: {policy_name}")

    llm_client = LLMClient(
        model=llm_config.get("model"),
        temperature=float(llm_config.get("temperature", 0.0)),
        mock=bool(args.mock or llm_config.get("mock", False)),
    )
    tools = AgentTools(
        retrieval=RetrievalTool(embedding_model=str(models.get("embedding_model", "BAAI/bge-small-en-v1.5"))),
        rerank=RerankTool(
            model_name=str(reranker_config.get("model", "BAAI/bge-reranker-base")),
            backend=str(reranker_config.get("backend", "auto")),
            fallback=bool(reranker_config.get("fallback", True)),
        ),
        rewrite=QueryRewriteTool(llm_client),
        answer=AnswerTool(
            AnswerGenerator(
                llm_client,
                max_context_chunks=int(generation_config.get("max_context_chunks", 5)),
            )
        ),
        refusal=RefusalTool(),
    )
    policy = EvidencePolicy(
        EvidencePolicyConfig(
            min_top_rerank_score=float(selected_policy.get("min_top_rerank_score", 0.5)),
            min_supporting_chunks=int(selected_policy.get("min_supporting_chunks", 1)),
            max_retries=int(selected_policy.get("max_retries", 1)),
            weak_evidence_margin=float(selected_policy.get("weak_evidence_margin", 0.1)),
        )
    )
    executor = RagAgentExecutor(
        planner=AgentPlanner(),
        policy=policy,
        tools=tools,
        index_dir=args.index_dir,
        initial_top_k=int(retrieval_config.get("initial_top_k", retrieval_config.get("retrieve_k", 10))),
        rerank_top_n=int(retrieval_config.get("rerank_top_n", 5)),
    )
    trace = executor.run(args.question)

    final = trace["final_answer"] or {}
    rewrite_used = bool(trace.get("rewritten_query"))
    latest_rerank = trace["rerank_results"][-1]["reranked_chunks"] if trace["rerank_results"] else []

    trace_path = None
    if args.save_trace:
        trace_path = AgentTraceLogger().save(trace, args.save_trace)

    print("\nQuestion")
    print(trace["original_question"])
    print("\nQuery Type")
    print(trace["query_type"])
    print("\nFinal Decision")
    print(trace["final_decision"])
    print("\nAgent Policy")
    print(policy_name)
    print("\nAnswer")
    print(final.get("answer"))
    print("\nQuery Rewrite Used")
    print("yes" if rewrite_used else "no")
    if rewrite_used:
        print(f"rewritten_query={trace['rewritten_query']}")
    print("\nTop Evidence")
    for index, chunk in enumerate(latest_rerank[:5], start=1):
        metadata = chunk.get("metadata", {})
        print(
            f"{index}. retrieval_score={chunk.get('retrieval_score')} "
            f"rerank_score={chunk.get('rerank_score')} "
            f"section={metadata.get('section_title')} "
            f"source={metadata.get('file_name')} "
            f"chunk_id={chunk.get('chunk_id')}"
        )
    if trace_path:
        print("\nTrace Path")
        print(trace_path)


if __name__ == "__main__":
    main()
