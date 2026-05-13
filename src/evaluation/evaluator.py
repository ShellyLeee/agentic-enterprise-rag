"""Three-system evaluation runner for Naive, Rerank, and Agentic RAG."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from src.agent import AgentPlanner, AgentTools, EvidenceLoopConfig, EvidencePolicy, EvidencePolicyConfig, RagAgentExecutor
from src.evaluation.dataset import EvalQuestion, load_eval_dataset
from src.evaluation.metrics import (
    exact_match,
    is_refusal,
    keyword_alignment,
    mean,
    retrieval_hit_at_k,
    token_f1,
    unsupported_answer_proxy,
)
from src.generation.answer_generator import AnswerGenerator
from src.generation.llm_client import LLMClient
from src.retrieval.reranker import Reranker
from src.retrieval.retriever import Retriever
from src.tools import AnswerTool, QueryRewriteTool, RefusalTool, RerankTool, RetrievalTool


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluatorConfig:
    """Runtime settings shared by evaluation methods."""

    index_dir: str
    embedding_model: str
    reranker_model: str
    reranker_backend: str
    reranker_fallback: bool
    retrieve_k: int
    rerank_top_n: int
    max_context_chunks: int
    llm_model: str
    llm_temperature: float
    mock: bool
    agent_score_mode: str
    agent_min_top_retrieval_score: float
    agent_min_top_rerank_score: float
    agent_min_supporting_chunks: int
    agent_max_retries: int
    agent_weak_evidence_margin: float
    agent_policy_name: str = "balanced"
    agent_policy_presets: dict[str, dict[str, Any]] | None = None
    evidence_loop_enabled: bool = True
    evidence_loop_max_followup_queries: int = 2
    evidence_loop_followup_top_k: int = 5
    evidence_loop_followup_rerank_top_n: int = 3
    evidence_loop_merge_strategy: str = "append_top_unique"
    evidence_loop_min_gap_detection_score: float = 0.0


@dataclass
class EvaluationRuntime:
    """Shared components constructed once per evaluation run."""

    retriever: Retriever
    reranker: Reranker | None
    llm_client: LLMClient
    answer_generator: AnswerGenerator
    agent_tools: AgentTools | None
    agent_executors: dict[str, RagAgentExecutor]


class ThreeSystemEvaluator:
    """Evaluate Naive RAG, RAG+Reranker, and Agentic RAG on one dataset."""

    def __init__(self, config: EvaluatorConfig) -> None:
        self.config = config

    def run(
        self,
        eval_file: str | Path,
        methods: list[str],
        output_dir: str | Path,
        agent_policies: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run selected methods and write evaluation artifacts."""
        rows = load_eval_dataset(eval_file)
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        all_metrics = {}
        all_results = {}
        expanded_methods = self._expand_methods(methods, agent_policies)
        runtime = self._build_runtime(expanded_methods)
        for method in expanded_methods:
            method = method.strip()
            if not method:
                continue
            LOGGER.info("Running method %s", method)
            results = [self._run_one(method, row, runtime) for row in rows]
            metrics = self._aggregate(method, rows, results)
            all_metrics[method] = metrics
            all_results[method] = results
            (output / f"metrics_{method}.json").write_text(
                json.dumps({"metrics": metrics, "results": results}, indent=2),
                encoding="utf-8",
            )

        (output / "comparison_table.md").write_text(
            self._comparison_table(all_metrics),
            encoding="utf-8",
        )
        (output / "error_cases.md").write_text(
            self._error_cases(rows, all_results),
            encoding="utf-8",
        )
        return all_metrics

    def _run_one(self, method: str, row: EvalQuestion, runtime: EvaluationRuntime) -> dict[str, Any]:
        """Run one method on one question and return raw result plus metrics inputs."""
        started = perf_counter()
        if method == "naive":
            result = self._run_naive(row.question, runtime)
        elif method == "rerank":
            result = self._run_rerank(row.question, runtime)
        elif method == "agentic":
            result = self._run_agentic(row.question, self.config.agent_policy_name, runtime)
        elif method.startswith("agentic_"):
            result = self._run_agentic(row.question, method.removeprefix("agentic_"), runtime)
        else:
            raise ValueError(f"Unsupported eval method: {method}")
        result["latency_seconds"] = round(perf_counter() - started, 4)
        result["id"] = row.id
        result["question"] = row.question
        result["gold_answer"] = row.answer
        result["type"] = row.type
        result["mock_mode"] = self.config.mock
        return result

    def _run_naive(self, question: str, runtime: EvaluationRuntime) -> dict[str, Any]:
        """Run baseline A."""
        retrieved = runtime.retriever.retrieve(question, top_k=self.config.rerank_top_n)
        answer = runtime.answer_generator.generate(question, retrieved)
        return {
            "answer": answer.answer,
            "decision": "answer",
            "retrieved_chunks": retrieved,
            "evidence_used": answer.retrieved_chunks,
            "citations": answer.citations,
            "system": "naive",
        }

    def _run_rerank(self, question: str, runtime: EvaluationRuntime) -> dict[str, Any]:
        """Run baseline B."""
        if runtime.reranker is None:
            raise RuntimeError("Reranker was not initialized for rerank evaluation.")
        reranker = runtime.reranker
        retrieved = runtime.retriever.retrieve(question, top_k=self.config.retrieve_k)
        reranked = reranker.rerank(question, retrieved, top_n=self.config.rerank_top_n)
        answer = runtime.answer_generator.generate(question, reranked)
        return {
            "answer": answer.answer,
            "decision": "answer",
            "retrieved_chunks": retrieved,
            "evidence_used": answer.retrieved_chunks,
            "reranker_backend": reranker.backend_used,
            "citations": answer.citations,
            "system": "rerank",
        }

    def _run_agentic(self, question: str, policy_name: str, runtime: EvaluationRuntime) -> dict[str, Any]:
        """Run agentic workflow."""
        executor = runtime.agent_executors.get(policy_name)
        if executor is None:
            raise RuntimeError(f"Agent executor was not initialized for policy: {policy_name}")
        trace = executor.run(question)
        final = trace.get("final_answer") or {}
        latest_retrieval = trace["retrieval_results"][-1]["retrieved_chunks"] if trace["retrieval_results"] else []
        evidence_used = final.get("evidence_used") or trace["rerank_results"][-1]["reranked_chunks"]
        return {
            "answer": final.get("answer"),
            "decision": trace.get("final_decision"),
            "query_type": trace.get("query_type"),
            "retrieved_chunks": latest_retrieval,
            "evidence_used": evidence_used,
            "citations": final.get("citations", []),
            "retry_count": trace.get("retry_count", 0),
            "policy_name": policy_name,
            "system": f"agentic_{policy_name}",
        }

    def _build_runtime(self, expanded_methods: list[str]) -> EvaluationRuntime:
        """Initialize shared retriever, reranker, LLM, tools, and agent executors once."""
        LOGGER.info("Initializing shared retriever...")
        retriever = Retriever.load(self.config.index_dir, embedding_model=self.config.embedding_model)

        needs_reranker = any(method == "rerank" or method == "agentic" or method.startswith("agentic_") for method in expanded_methods)
        reranker = None
        if needs_reranker:
            LOGGER.info("Initializing shared reranker...")
            reranker = Reranker(
                model_name=self.config.reranker_model,
                backend=self.config.reranker_backend,
                fallback=self.config.reranker_fallback,
            )

        llm_client = self._llm_client()
        answer_generator = AnswerGenerator(llm_client, max_context_chunks=self.config.max_context_chunks)

        agent_policy_names = self._agent_policy_names(expanded_methods)
        agent_tools = None
        agent_executors: dict[str, RagAgentExecutor] = {}
        if agent_policy_names:
            if reranker is None:
                raise RuntimeError("Reranker was not initialized for agentic evaluation.")
            agent_tools = AgentTools(
                retrieval=RetrievalTool(embedding_model=self.config.embedding_model, retriever=retriever),
                rerank=RerankTool(
                    model_name=self.config.reranker_model,
                    backend=self.config.reranker_backend,
                    fallback=self.config.reranker_fallback,
                    reranker=reranker,
                ),
                rewrite=QueryRewriteTool(llm_client),
                answer=AnswerTool(answer_generator),
                refusal=RefusalTool(),
            )
            for policy_name in agent_policy_names:
                agent_executors[policy_name] = self._build_agent_executor(policy_name, agent_tools)

        return EvaluationRuntime(
            retriever=retriever,
            reranker=reranker,
            llm_client=llm_client,
            answer_generator=answer_generator,
            agent_tools=agent_tools,
            agent_executors=agent_executors,
        )

    def _build_agent_executor(self, policy_name: str, tools: AgentTools) -> RagAgentExecutor:
        """Build one agent executor for a policy preset."""
        policy_config = self._agent_policy_config(policy_name)
        return RagAgentExecutor(
            planner=AgentPlanner(),
            policy=EvidencePolicy(
                EvidencePolicyConfig(
                    score_mode=str(policy_config.get("score_mode", self.config.agent_score_mode)),
                    min_top_retrieval_score=float(
                        policy_config.get("min_top_retrieval_score", self.config.agent_min_top_retrieval_score)
                    ),
                    min_top_rerank_score=float(policy_config.get("min_top_rerank_score", self.config.agent_min_top_rerank_score)),
                    min_supporting_chunks=int(policy_config.get("min_supporting_chunks", self.config.agent_min_supporting_chunks)),
                    max_retries=int(policy_config.get("max_retries", self.config.agent_max_retries)),
                    weak_evidence_margin=float(policy_config.get("weak_evidence_margin", self.config.agent_weak_evidence_margin)),
                )
            ),
            tools=tools,
            index_dir=self.config.index_dir,
            initial_top_k=self.config.retrieve_k,
            rerank_top_n=self.config.rerank_top_n,
            evidence_loop=EvidenceLoopConfig(
                enabled=self.config.evidence_loop_enabled,
                max_followup_queries=self.config.evidence_loop_max_followup_queries,
                followup_top_k=self.config.evidence_loop_followup_top_k,
                followup_rerank_top_n=self.config.evidence_loop_followup_rerank_top_n,
                merge_strategy=self.config.evidence_loop_merge_strategy,
                min_gap_detection_score=self.config.evidence_loop_min_gap_detection_score,
            ),
        )

    def _aggregate(
        self,
        method: str,
        rows: list[EvalQuestion],
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate transparent metrics for one method."""
        per_question = []
        for row, result in zip(rows, results):
            answer = result.get("answer")
            retrieved = result.get("retrieved_chunks", [])
            evidence = result.get("evidence_used", retrieved)
            decision = result.get("decision")
            refused = is_refusal(answer, decision)
            answerable = row.type != "ood"
            row_metrics = {
                "id": row.id,
                "type": row.type,
                "exact_match": exact_match(answer, row.answer),
                "token_f1": token_f1(answer, row.answer),
                "retrieval_hit_at_k": retrieval_hit_at_k(retrieved, row.gold_evidence_keywords, self.config.rerank_top_n),
                "keyword_alignment": keyword_alignment(answer, evidence, row.gold_evidence_keywords),
                "is_refusal": 1.0 if refused else 0.0,
                "is_answer": 0.0 if refused else 1.0,
                "false_refusal": 1.0 if answerable and refused else 0.0,
                "false_answer": 1.0 if row.type == "ood" and not refused else 0.0,
                "refusal_correct": 1.0
                if row.type == "ood" and refused
                else (1.0 if answerable and not refused else 0.0),
                "unsupported_answer_proxy": unsupported_answer_proxy(
                    answer,
                    evidence,
                    row.gold_evidence_keywords,
                    decision,
                ),
                "latency_seconds": result.get("latency_seconds", 0.0),
            }
            per_question.append(row_metrics)

        answerable_items = [item for item in per_question if item["type"] != "ood"]
        simple = [item["token_f1"] for item in per_question if item["type"] == "simple"]
        comparison = [item["token_f1"] for item in per_question if item["type"] == "comparison"]
        multi_hop = [item["token_f1"] for item in per_question if item["type"] == "multi_hop"]
        ood = [item for item in per_question if item["type"] == "ood"]
        return {
            "method": method,
            "mock_mode": self.config.mock,
            "note": "Smoke-test metrics on a tiny sample dataset; do not treat as benchmark results.",
            "num_questions": len(rows),
            "exact_match": mean([item["exact_match"] for item in per_question]),
            "token_f1": mean([item["token_f1"] for item in per_question]),
            "overall_f1": mean([item["token_f1"] for item in per_question]),
            "answerable_f1": mean([item["token_f1"] for item in answerable_items]),
            "simple_f1": mean(simple),
            "comparison_f1": mean(comparison),
            "multi_hop_f1": mean(multi_hop),
            "retrieval_hit_at_k": mean([item["retrieval_hit_at_k"] for item in per_question]),
            "multi_hop_subset_f1": mean(multi_hop),
            "refusal_accuracy": mean([item["refusal_correct"] for item in ood]),
            "ood_refusal_accuracy": mean([item["refusal_correct"] for item in ood]),
            "unsupported_answer_proxy_rate": mean([item["unsupported_answer_proxy"] for item in per_question]),
            "unsupported_rate": mean([item["unsupported_answer_proxy"] for item in per_question]),
            "answer_rate": mean([item["is_answer"] for item in per_question]),
            "refusal_rate": mean([item["is_refusal"] for item in per_question]),
            "false_refusal_count": int(sum(item["false_refusal"] for item in per_question)),
            "false_answer_count": int(sum(item["false_answer"] for item in per_question)),
            "avg_latency_seconds": mean([item["latency_seconds"] for item in per_question]),
            "per_question": per_question,
        }

    @staticmethod
    def _expand_methods(methods: list[str], agent_policies: list[str] | None) -> list[str]:
        """Expand `agentic` into one method per requested policy preset."""
        expanded: list[str] = []
        policies = agent_policies or []
        for method in methods:
            if method == "agentic" and policies:
                expanded.extend([f"agentic_{policy}" for policy in policies])
            else:
                expanded.append(method)
        return expanded

    def _agent_policy_names(self, expanded_methods: list[str]) -> list[str]:
        """Return unique agent policy names needed by expanded methods."""
        policy_names: list[str] = []
        for method in expanded_methods:
            if method == "agentic":
                policy_name = self.config.agent_policy_name
            elif method.startswith("agentic_"):
                policy_name = method.removeprefix("agentic_")
            else:
                continue
            if policy_name not in policy_names:
                policy_names.append(policy_name)
        return policy_names

    def _agent_policy_config(self, policy_name: str) -> dict[str, Any]:
        """Return policy thresholds for a named preset, falling back to config values."""
        presets = self.config.agent_policy_presets or {}
        if policy_name in presets:
            return presets[policy_name]
        if policy_name != self.config.agent_policy_name and presets:
            raise ValueError(f"Unknown agent policy preset: {policy_name}")
        return {
            "score_mode": self.config.agent_score_mode,
            "min_top_retrieval_score": self.config.agent_min_top_retrieval_score,
            "min_top_rerank_score": self.config.agent_min_top_rerank_score,
            "min_supporting_chunks": self.config.agent_min_supporting_chunks,
            "max_retries": self.config.agent_max_retries,
            "weak_evidence_margin": self.config.agent_weak_evidence_margin,
        }

    def _llm_client(self) -> LLMClient:
        """Create an LLM client for generation/rewrite."""
        return LLMClient(
            model=self.config.llm_model,
            temperature=self.config.llm_temperature,
            mock=self.config.mock,
        )

    @staticmethod
    def _comparison_table(all_metrics: dict[str, dict[str, Any]]) -> str:
        """Render method metrics as markdown."""
        headers = [
            "method",
            "mock",
            "EM",
            "overall_f1",
            "answerable_f1",
            "simple_f1",
            "comparison_f1",
            "multi_hop_f1",
            "Hit@k",
            "ood_refusal_accuracy",
            "unsupported_rate",
            "answer_rate",
            "refusal_rate",
            "false_refusals",
            "false_answers",
            "Avg latency",
        ]
        lines = [
            "# Evaluation Comparison",
            "",
            "Smoke-test metrics on a tiny sample dataset; not benchmark results.",
            "",
            "Agentic methods include iterative evidence-seeking when enabled in the run configuration.",
            "",
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for method, metrics in all_metrics.items():
            lines.append(
                "| "
                + " | ".join(
                    [
                        method,
                        str(metrics["mock_mode"]),
                        f"{metrics['exact_match']:.3f}",
                        f"{metrics['overall_f1']:.3f}",
                        f"{metrics['answerable_f1']:.3f}",
                        f"{metrics['simple_f1']:.3f}",
                        f"{metrics['comparison_f1']:.3f}",
                        f"{metrics['multi_hop_f1']:.3f}",
                        f"{metrics['retrieval_hit_at_k']:.3f}",
                        f"{metrics['ood_refusal_accuracy']:.3f}",
                        f"{metrics['unsupported_rate']:.3f}",
                        f"{metrics['answer_rate']:.3f}",
                        f"{metrics['refusal_rate']:.3f}",
                        str(metrics["false_refusal_count"]),
                        str(metrics["false_answer_count"]),
                        f"{metrics['avg_latency_seconds']:.3f}",
                    ]
                )
                + " |"
            )
        return "\n".join(lines) + "\n"

    @staticmethod
    def _error_cases(rows: list[EvalQuestion], all_results: dict[str, list[dict[str, Any]]]) -> str:
        """Render grouped error and analysis cases as markdown."""
        lines = [
            "# Error Cases",
            "",
            "Grouped smoke-test diagnostics. These are lexical/proxy checks, not human judgments.",
            "",
        ]
        row_by_id = {row.id: row for row in rows}
        for method, results in all_results.items():
            lines.extend([f"## {method}", ""])
            groups = {
                "False refusals on answerable questions": [],
                "False answers on OOD questions": [],
                "Low-F1 answered cases": [],
                "Retrieval misses": [],
                "Unsupported answers": [],
            }
            for result in results:
                row = row_by_id[result["id"]]
                answer = result.get("answer")
                decision = result.get("decision")
                refused = is_refusal(answer, decision)
                f1 = token_f1(answer, row.answer)
                retrieval_hit = retrieval_hit_at_k(
                    result.get("retrieved_chunks", []),
                    row.gold_evidence_keywords,
                    5,
                )
                unsupported = unsupported_answer_proxy(
                    answer,
                    result.get("evidence_used", []),
                    row.gold_evidence_keywords,
                    decision,
                )
                case = {
                    "row": row,
                    "result": result,
                    "f1": f1,
                    "retrieval_hit": retrieval_hit,
                    "unsupported": unsupported,
                }
                if row.type != "ood" and refused:
                    groups["False refusals on answerable questions"].append(case)
                if row.type == "ood" and not refused:
                    groups["False answers on OOD questions"].append(case)
                if row.type != "ood" and not refused and f1 < 0.25:
                    groups["Low-F1 answered cases"].append(case)
                if retrieval_hit == 0.0:
                    groups["Retrieval misses"].append(case)
                if unsupported:
                    groups["Unsupported answers"].append(case)

            for group_name, cases in groups.items():
                lines.extend([f"### {group_name}", ""])
                if not cases:
                    lines.extend(["- None.", ""])
                    continue
                for case in cases:
                    row = case["row"]
                    result = case["result"]
                    lines.extend(
                        [
                            f"- `{row.id}` ({row.type})",
                            f"  - question: {row.question}",
                            f"  - gold: {row.answer}",
                            f"  - predicted: {result.get('answer')}",
                            f"  - decision: {result.get('decision')}",
                            f"  - f1: {case['f1']:.3f}",
                            f"  - retrieval_hit: {case['retrieval_hit']}",
                            f"  - unsupported_proxy: {case['unsupported']}",
                            "",
                        ]
                    )
        return "\n".join(lines)
