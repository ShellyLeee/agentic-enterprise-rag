"""Run three-system RAG evaluation."""

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

from src.evaluation import EvaluatorConfig, ThreeSystemEvaluator


LOGGER = logging.getLogger(__name__)


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Evaluate naive, rerank, and agentic RAG methods.")
    parser.add_argument("--eval_file", required=True, help="Evaluation JSONL path.")
    parser.add_argument("--methods", default="naive,rerank,agentic", help="Comma-separated methods.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Vector index dir.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force mock LLM mode.")
    parser.add_argument("--output_dir", default="results/eval_sample", help="Output directory.")
    parser.add_argument(
        "--agent_policies",
        default="",
        help="Comma-separated agent policy presets to sweep when method includes agentic.",
    )
    parser.add_argument("--disable_evidence_loop", action="store_true", help="Disable agentic iterative evidence seeking.")
    return parser


def evaluator_config(config: dict[str, Any], args: argparse.Namespace) -> EvaluatorConfig:
    """Build evaluator config from YAML and CLI."""
    models = config.get("models", {})
    retrieval = config.get("retrieval", {})
    reranker = config.get("reranker", {})
    generation = config.get("generation", {})
    llm = config.get("llm", {})
    agent = config.get("agent", {})
    metadata = config.get("metadata", {})
    evidence_loop = agent.get("evidence_loop", {})
    policy_presets = agent.get("policy_presets", {})
    default_policy = str(agent.get("default_policy", "balanced"))
    selected_policy = policy_presets.get(default_policy, {})
    return EvaluatorConfig(
        index_dir=args.index_dir,
        embedding_model=str(models.get("embedding_model", "BAAI/bge-small-en-v1.5")),
        reranker_model=str(reranker.get("model", "BAAI/bge-reranker-base")),
        reranker_backend=str(reranker.get("backend", "auto")),
        reranker_fallback=bool(reranker.get("fallback", True)),
        retrieve_k=int(retrieval.get("retrieve_k", 10)),
        rerank_top_n=int(retrieval.get("rerank_top_n", 5)),
        max_context_chunks=int(generation.get("max_context_chunks", 5)),
        llm_model=str(llm.get("model", "gpt-4o-mini")),
        llm_temperature=float(llm.get("temperature", 0.0)),
        mock=bool(args.mock or llm.get("mock", False)),
        agent_score_mode=str(selected_policy.get("score_mode", agent.get("score_mode", "hybrid"))),
        agent_min_top_retrieval_score=float(
            selected_policy.get("min_top_retrieval_score", agent.get("min_top_retrieval_score", 0.65))
        ),
        agent_min_top_rerank_score=float(selected_policy.get("min_top_rerank_score", agent.get("min_top_rerank_score", 0.005))),
        agent_min_supporting_chunks=int(selected_policy.get("min_supporting_chunks", agent.get("min_supporting_chunks", 1))),
        agent_max_retries=int(selected_policy.get("max_retries", agent.get("max_retries", 1))),
        agent_weak_evidence_margin=float(selected_policy.get("weak_evidence_margin", agent.get("weak_evidence_margin", 0.1))),
        agent_policy_name=default_policy,
        agent_policy_presets=policy_presets,
        evidence_loop_enabled=bool(evidence_loop.get("enabled", True)) and not bool(args.disable_evidence_loop),
        evidence_loop_max_followup_queries=int(evidence_loop.get("max_followup_queries", 2)),
        evidence_loop_followup_top_k=int(evidence_loop.get("followup_top_k", 5)),
        evidence_loop_followup_rerank_top_n=int(evidence_loop.get("followup_rerank_top_n", 3)),
        evidence_loop_merge_strategy=str(evidence_loop.get("merge_strategy", "append_top_unique")),
        evidence_loop_min_gap_detection_score=float(evidence_loop.get("min_gap_detection_score", 0.0)),
        metadata_subset_csv=metadata.get("subset_csv"),
    )


def main() -> None:
    """Run evaluation and print summary metrics."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    agent_policies = [policy.strip() for policy in args.agent_policies.split(",") if policy.strip()]
    LOGGER.info("Starting evaluation run...")
    metrics = ThreeSystemEvaluator(evaluator_config(config, args)).run(
        eval_file=args.eval_file,
        methods=methods,
        output_dir=args.output_dir,
        agent_policies=agent_policies,
    )
    print(json.dumps(metrics, indent=2))
    print(f"\nWrote evaluation artifacts to {args.output_dir}")


if __name__ == "__main__":
    main()
