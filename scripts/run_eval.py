"""Run benchmark or legacy smoke-test evaluation."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - convenience fallback for minimal environments
    def tqdm(iterable: Any, **_: Any) -> Any:
        return iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eval import (
    QAExample,
    boolean_accuracy_score,
    detect_abstention,
    evidence_recall_at_k,
    exact_match_score,
    f1_score,
    load_financebench,
    load_hotpotqa,
    mrr,
    numeric_match_score,
    retrieval_hit_at_k,
)
from src.eval.categories import categorize_example
from src.evaluation import EvaluatorConfig, ThreeSystemEvaluator
from src.llm import LLMClient, LLMGeneration
from src.prompts.qa_prompts import system_prompt_for_setting, user_prompt
from src.retrieval.reranker import Reranker
from src.retrieval.simple_retriever import SimpleRetriever


LOGGER = logging.getLogger(__name__)
BENCHMARK_SETTINGS = (
    "no_rag",
    "rag",
    "basic_rag",
    "reranker_rag",
    "agentic_rag_conservative",
    "agentic_rag_balanced",
    "agentic_rag_aggressive",
)


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Run benchmark or legacy RAG evaluation.")
    parser.add_argument("--config", default="configs/default.yaml", help="YAML config path.")
    parser.add_argument("--mock", action="store_true", help="Force deterministic mock LLM mode.")

    parser.add_argument("--dataset", choices=["hotpotqa", "financebench"], help="Benchmark dataset.")
    parser.add_argument("--setting", choices=BENCHMARK_SETTINGS, help="Benchmark setting.")
    parser.add_argument("--max_examples", type=int, help="Maximum benchmark examples.")
    parser.add_argument("--top_k", type=int, help="Top-k retrieved documents for RAG benchmark.")
    parser.add_argument("--retrieve_top_n", type=int, default=20, help="Initial retrieval depth for reranker RAG.")
    parser.add_argument("--rerank_top_k", type=int, default=5, help="Final reranked context size.")
    parser.add_argument("--evidence_threshold", type=float, help="Minimum retrieval score for agentic abstention policy.")
    parser.add_argument("--numeric_tolerance", type=float, default=0.02, help="Relative tolerance for numeric match.")
    parser.add_argument("--split", default="validation", help="HotpotQA split.")
    parser.add_argument(
        "--financebench_source",
        choices=["hf", "local", "auto"],
        default="hf",
        help="FinanceBench source: HuggingFace, local file/directory, or HuggingFace with local fallback.",
    )
    parser.add_argument(
        "--financebench_local_path",
        help="Local FinanceBench JSON/JSONL/CSV file or directory used with source=local/auto.",
    )
    parser.add_argument(
        "--financebench_dir",
        default="data/financebench",
        help="Deprecated alias for --financebench_local_path.",
    )
    parser.add_argument(
        "--financebench_mode",
        choices=["evidence", "pdf"],
        default="evidence",
        help="FinanceBench corpus mode. Current implementation supports evidence; pdf is a future extension point.",
    )
    parser.add_argument("--output_dir", help="Benchmark output directory.")

    parser.add_argument("--eval_file", help="Legacy evaluation JSONL path.")
    parser.add_argument("--methods", default="naive,rerank,agentic", help="Legacy comma-separated methods.")
    parser.add_argument("--index_dir", default="data/processed/vector_index", help="Legacy vector index dir.")
    parser.add_argument(
        "--agent_policies",
        default="",
        help="Legacy comma-separated agent policy presets to sweep when method includes agentic.",
    )
    parser.add_argument("--disable_evidence_loop", action="store_true", help="Disable legacy evidence loop.")
    return parser


def main() -> None:
    """Run the requested evaluation path."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    config = load_config(Path(args.config))

    if args.eval_file:
        _run_legacy_eval(config, args)
        return
    if not args.dataset or not args.setting:
        raise SystemExit("Provide --dataset and --setting for benchmark eval, or --eval_file for legacy eval.")
    if args.dataset == "financebench" and args.financebench_mode != "evidence":
        raise SystemExit("FinanceBench pdf mode is not implemented yet; use --financebench_mode evidence.")
    _run_benchmark_eval(config, args)


def _run_benchmark_eval(config: dict[str, Any], args: argparse.Namespace) -> None:
    """Run HotpotQA or FinanceBench benchmark evaluation."""
    eval_config = config.get("eval", config.get("evaluation", {}))
    max_examples = args.max_examples
    if max_examples is None:
        configured_max = eval_config.get("max_examples")
        max_examples = int(configured_max) if configured_max is not None else None
    top_k = int(args.top_k if args.top_k is not None else eval_config.get("top_k", 5))
    output_dir = Path(args.output_dir or eval_config.get("output_dir", "outputs/eval_results"))
    output_dir.mkdir(parents=True, exist_ok=True)
    setting = _normalize_setting(args.setting)

    examples = _load_examples(args.dataset, max_examples, args)
    llm_config = dict(config.get("llm", {}))
    if args.mock:
        llm_config["mock"] = True
    client = LLMClient({"llm": llm_config})

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result_path = output_dir / f"{args.dataset}_{setting}_{timestamp}.jsonl"
    summary_path = output_dir / f"{args.dataset}_{setting}_{timestamp}_summary.json"

    rows = []
    for example in tqdm(examples, desc=f"{args.dataset}:{setting}"):
        row = _run_one_benchmark_example(example, client, args.dataset, setting, top_k, args)
        rows.append(row)
        with result_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = _summarize(rows, args.dataset, setting, config, top_k)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_summary(summary, result_path, summary_path)


def _load_examples(dataset: str, max_examples: int | None, args: argparse.Namespace) -> list[QAExample]:
    """Load benchmark examples by dataset name."""
    if dataset == "hotpotqa":
        return load_hotpotqa(max_examples=max_examples, split=args.split)
    if dataset == "financebench":
        local_path = args.financebench_local_path or args.financebench_dir
        return load_financebench(
            max_examples=max_examples,
            source=args.financebench_source,
            local_path=local_path,
        )
    raise ValueError(f"Unsupported dataset: {dataset}")


def _run_one_benchmark_example(
    example: QAExample,
    client: LLMClient,
    dataset_name: str,
    setting: str,
    top_k: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Run one benchmark example and return a JSON-serializable row."""
    started = perf_counter()
    categories = categorize_example(example, dataset_name)
    retrieved_docs = _retrieve_for_setting(example, setting, top_k, args)
    weak_evidence = _has_weak_evidence(retrieved_docs, setting, args)
    generation = _generate_prediction(client, example, dataset_name, setting, retrieved_docs, weak_evidence)
    prediction = generation.prediction
    latency = perf_counter() - started
    boolean_acc = boolean_accuracy_score(prediction, example.answers)
    retrieval_hit = retrieval_hit_at_k(retrieved_docs, example.gold_evidence) if setting != "no_rag" else 0.0
    evidence_recall = evidence_recall_at_k(retrieved_docs, example.gold_evidence) if setting != "no_rag" else 0.0
    reciprocal_rank = mrr(retrieved_docs, example.gold_evidence) if setting != "no_rag" else 0.0
    return {
        "id": example.id,
        "question": example.question,
        "categories": categories,
        "gold_answers": example.answers,
        "prediction": prediction,
        "raw_prediction": generation.raw_prediction,
        "retrieved_docs": retrieved_docs,
        "em": exact_match_score(prediction, example.answers),
        "f1": f1_score(prediction, example.answers),
        "numeric_match": numeric_match_score(prediction, example.answers, tolerance=args.numeric_tolerance),
        "boolean_acc": boolean_acc,
        "abstained": detect_abstention(prediction),
        "retrieval_hit": retrieval_hit,
        "evidence_recall_at_k": evidence_recall,
        "mrr": reciprocal_rank,
        "weak_evidence": weak_evidence,
        "latency_sec": round(latency, 4),
        "metadata": example.metadata or {},
    }


def _retrieve_for_setting(
    example: QAExample,
    setting: str,
    top_k: int,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    """Retrieve context documents according to the requested benchmark setting."""
    if setting == "no_rag":
        return []

    retriever = SimpleRetriever()
    retriever.index(example.documents or [])
    if setting == "reranker_rag":
        candidates = retriever.retrieve(example.question, top_k=args.retrieve_top_n)
        reranker = Reranker(backend="fallback")
        return reranker.rerank(example.question, candidates, top_n=args.rerank_top_k)
    return retriever.retrieve(example.question, top_k=top_k)


def _has_weak_evidence(
    retrieved_docs: list[dict[str, Any]],
    setting: str,
    args: argparse.Namespace,
) -> bool:
    """Return true when agentic policies should abstain before calling the LLM."""
    if not setting.startswith("agentic_rag"):
        return False
    if not retrieved_docs:
        return True
    threshold = args.evidence_threshold
    if threshold is None:
        threshold = {
            "agentic_rag_conservative": 0.15,
            "agentic_rag_balanced": 0.05,
            "agentic_rag_aggressive": 0.0,
        }.get(setting, 0.05)
    best_score = max(float(doc.get("score", doc.get("retrieval_score", 0.0)) or 0.0) for doc in retrieved_docs)
    return best_score < threshold


def _generate_prediction(
    client: LLMClient,
    example: QAExample,
    dataset_name: str,
    setting: str,
    retrieved_docs: list[dict[str, Any]],
    weak_evidence: bool,
) -> LLMGeneration:
    """Generate an answer using optional retrieved context."""
    if weak_evidence and setting == "agentic_rag_conservative":
        answer = "Not sure based on the provided context."
        return LLMGeneration(prediction=answer, raw_prediction=answer, model=client.model_name, mode="policy-abstain")
    context = _format_context(retrieved_docs)
    prompt = user_prompt(example.question, context, setting)
    system_prompt = system_prompt_for_setting(setting, example, dataset_name)
    return client.generate_from_prompt_with_raw(prompt, system_prompt=system_prompt)


def _format_context(documents: list[dict[str, Any]]) -> str:
    """Render retrieved documents into a compact prompt context."""
    parts = []
    for index, document in enumerate(documents, start=1):
        parts.append(
            f"[chunk:{index}:{document.get('chunk_id', index)}]\n"
            f"title: {document.get('title', '')}\n"
            f"source: {document.get('source', '')}\n"
            f"score: {document.get('score')}\n"
            f"text: {document.get('text', '')}"
        )
    return "\n\n---\n\n".join(parts)


def _summarize(
    rows: list[dict[str, Any]],
    dataset: str,
    setting: str,
    config: dict[str, Any],
    top_k: int,
) -> dict[str, Any]:
    """Aggregate benchmark metrics."""
    count = len(rows)
    overall = _aggregate_rows(rows)
    return {
        "dataset": dataset,
        "setting": setting,
        **overall,
        "overall": overall,
        "by_category": _summarize_by_category(rows),
        "config": {
            "llm": _safe_llm_config(config.get("llm", {})),
            "eval": {**config.get("eval", {}), "top_k": top_k},
            "financebench_mode": "evidence",
        },
    }


def _safe_llm_config(llm_config: dict[str, Any]) -> dict[str, Any]:
    """Return LLM config with secrets redacted."""
    safe = dict(llm_config)
    if safe.get("api_key") and safe["api_key"] != "EMPTY":
        safe["api_key"] = "***"
    return safe


def _print_summary(summary: dict[str, Any], result_path: Path, summary_path: Path) -> None:
    """Print a compact summary table."""
    print("\nBenchmark Summary")
    print("| metric | value |")
    print("| --- | ---: |")
    for key in (
        "dataset",
        "setting",
        "num_examples",
        "avg_em",
        "avg_f1",
        "numeric_match",
        "boolean_acc",
        "retrieval_hit_rate",
        "evidence_recall_at_k",
        "mrr",
        "abstention_rate",
        "avg_latency_sec",
    ):
        value = summary[key]
        formatted = f"{value:.4f}" if isinstance(value, float) else str(value)
        print(f"| {key} | {formatted} |")
    if summary.get("by_category"):
        print("\nCategory Summary")
        print("| category | n | EM | F1 | numeric | boolean | hit | recall | mrr | abstain |")
        print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for category, metrics in sorted(summary["by_category"].items()):
            print(
                f"| {category} | {metrics['num_examples']} | {metrics['avg_em']:.4f} | "
                f"{metrics['avg_f1']:.4f} | {metrics['numeric_match']:.4f} | "
                f"{metrics['boolean_acc']:.4f} | {metrics['retrieval_hit_rate']:.4f} | "
                f"{metrics['evidence_recall_at_k']:.4f} | {metrics['mrr']:.4f} | "
                f"{metrics['abstention_rate']:.4f} |"
            )
    print(f"\nWrote per-example results to {result_path}")
    print(f"Wrote summary to {summary_path}")


def _mean(values: list[float]) -> float:
    """Safe arithmetic mean."""
    return round(sum(values) / len(values), 6) if values else 0.0


def _mean_present(values: list[float | None]) -> float:
    """Mean over non-null values."""
    present = [value for value in values if value is not None]
    return _mean(present)


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate all metrics for a row subset."""
    return {
        "num_examples": len(rows),
        "avg_em": _mean([row["em"] for row in rows]),
        "avg_f1": _mean([row["f1"] for row in rows]),
        "numeric_match": _mean([row["numeric_match"] for row in rows]),
        "boolean_acc": _mean_present([row["boolean_acc"] for row in rows]),
        "retrieval_hit_rate": _mean([row["retrieval_hit"] for row in rows]),
        "evidence_recall_at_k": _mean([row["evidence_recall_at_k"] for row in rows]),
        "mrr": _mean([row["mrr"] for row in rows]),
        "abstention_rate": _mean([1.0 if row["abstained"] else 0.0 for row in rows]),
        "avg_latency_sec": _mean([row["latency_sec"] for row in rows]),
    }


def _summarize_by_category(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate metrics for every category tag in the run."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for category in row.get("categories", []):
            grouped.setdefault(category, []).append(row)
    return {category: _aggregate_rows(category_rows) for category, category_rows in grouped.items()}


def _normalize_setting(setting: str) -> str:
    """Map backward-compatible setting aliases to canonical names."""
    return "basic_rag" if setting == "rag" else setting


def _run_legacy_eval(config: dict[str, Any], args: argparse.Namespace) -> None:
    """Run the original three-system smoke-test evaluator."""
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    agent_policies = [policy.strip() for policy in args.agent_policies.split(",") if policy.strip()]
    output_dir = args.output_dir or "results/eval_sample"
    LOGGER.info("Starting legacy evaluation run...")
    metrics = ThreeSystemEvaluator(_legacy_evaluator_config(config, args)).run(
        eval_file=args.eval_file,
        methods=methods,
        output_dir=output_dir,
        agent_policies=agent_policies,
    )
    print(json.dumps(metrics, indent=2))
    print(f"\nWrote evaluation artifacts to {output_dir}")


def _legacy_evaluator_config(config: dict[str, Any], args: argparse.Namespace) -> EvaluatorConfig:
    """Build the original evaluator config from YAML and CLI."""
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
        llm_model=str(llm.get("model_name", llm.get("model", "qwen3-8b"))),
        llm_temperature=float(llm.get("temperature", 0.0)),
        mock=bool(args.mock or llm.get("mock", False)),
        llm_base_url=llm.get("base_url"),
        llm_api_key=llm.get("api_key"),
        llm_max_tokens=llm.get("max_tokens"),
        llm_timeout=llm.get("timeout"),
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


if __name__ == "__main__":
    main()
