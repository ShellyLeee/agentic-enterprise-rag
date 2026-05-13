"""Explicit evidence-aware Agentic RAG executor.

This module intentionally avoids hiding the workflow inside a black-box
LangChain AgentExecutor. The sequence is readable and traceable:
plan -> retrieve -> rerank -> evidence gap check -> policy
-> optional rewrite retry -> answer/refuse.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.agent.evidence_gap import EvidenceGapDetector
from src.agent.planner import AgentPlanner
from src.agent.policy import EvidencePolicy, PolicyResult
from src.tools import AnswerTool, QueryRewriteTool, RefusalTool, RerankTool, RetrievalTool


@dataclass
class AgentTools:
    """Tool bundle used by the executor."""

    retrieval: RetrievalTool
    rerank: RerankTool
    rewrite: QueryRewriteTool
    answer: AnswerTool
    refusal: RefusalTool


@dataclass(frozen=True)
class EvidenceLoopConfig:
    """Settings for one-round iterative evidence seeking."""

    enabled: bool = True
    max_followup_queries: int = 2
    followup_top_k: int = 5
    followup_rerank_top_n: int = 3
    merge_strategy: str = "append_top_unique"
    min_gap_detection_score: float = 0.0


class RagAgentExecutor:
    """Coordinates the evidence-aware Agentic RAG workflow."""

    def __init__(
        self,
        *,
        planner: AgentPlanner,
        policy: EvidencePolicy,
        tools: AgentTools,
        index_dir: str,
        initial_top_k: int,
        rerank_top_n: int,
        evidence_loop: EvidenceLoopConfig | None = None,
        gap_detector: EvidenceGapDetector | None = None,
    ) -> None:
        self.planner = planner
        self.policy = policy
        self.tools = tools
        self.index_dir = index_dir
        self.initial_top_k = initial_top_k
        self.rerank_top_n = rerank_top_n
        self.evidence_loop = evidence_loop or EvidenceLoopConfig(enabled=False)
        self.gap_detector = gap_detector or EvidenceGapDetector(
            min_gap_detection_score=self.evidence_loop.min_gap_detection_score
        )

    def run(self, question: str) -> dict[str, Any]:
        """Run the agent and return a structured trace."""
        plan = self.planner.plan(question)
        trace: dict[str, Any] = {
            "trace_id": str(uuid4()),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "original_question": question,
            "query_type": plan.query_type,
            "plan": {
                "steps": plan.steps,
                "rationale": plan.rationale,
            },
            "tool_calls": [],
            "retrieval_results": [],
            "rerank_results": [],
            "evidence_statistics": [],
            "evidence_gap_checks": [],
            "evidence_gap_detected": False,
            "missing_fields": [],
            "followup_queries": [],
            "followup_tool_calls": [],
            "merged_evidence_count": 0,
            "final_evidence_count": 0,
            "evidence_loop_improved_policy_decision": False,
            "rewritten_query": None,
            "final_decision": None,
            "final_answer": None,
            "retry_count": 0,
        }

        current_query = question
        retry_count = 0

        while True:
            retrieval_output = self.tools.retrieval.run(
                query=current_query,
                top_k=self.initial_top_k,
                index_dir=self.index_dir,
            )
            self._record_tool(trace, "RetrievalTool", retrieval_output)
            trace["retrieval_results"].append(retrieval_output)

            rerank_output = self.tools.rerank.run(
                query=current_query,
                retrieved_chunks=retrieval_output["retrieved_chunks"],
                top_n=self.rerank_top_n,
            )
            self._record_tool(trace, "RerankTool", rerank_output)
            trace["rerank_results"].append(rerank_output)

            evidence_chunks = rerank_output["reranked_chunks"]
            initial_policy_result = self.policy.evaluate(
                query_type=plan.query_type,
                reranked_chunks=evidence_chunks,
                retry_count=retry_count,
            )
            loop_had_gap = False

            if self.evidence_loop.enabled:
                loop_result = self._run_evidence_loop(
                    question=question,
                    current_query=current_query,
                    query_type=plan.query_type,
                    initial_evidence=evidence_chunks,
                    trace=trace,
                )
                evidence_chunks = loop_result["merged_evidence"]
                loop_had_gap = bool(loop_result["has_gap"])

            policy_result = self.policy.evaluate(
                query_type=plan.query_type,
                reranked_chunks=evidence_chunks,
                retry_count=retry_count,
            )
            if loop_had_gap:
                trace["evidence_loop_improved_policy_decision"] = (
                    initial_policy_result.decision != "answer" and policy_result.decision == "answer"
                )
            self._record_policy(trace, policy_result, retry_count)
            trace["final_evidence_count"] = len(evidence_chunks)

            if policy_result.decision == "answer":
                answer_output = self.tools.answer.run(
                    question=question,
                    evidence_chunks=evidence_chunks,
                )
                self._record_tool(trace, "AnswerTool", answer_output)
                trace["final_decision"] = "answer"
                trace["final_answer"] = answer_output
                break

            if policy_result.decision == "rewrite_and_retry":
                rewrite_output = self.tools.rewrite.run(
                    original_query=current_query,
                    reason=policy_result.reason,
                    failed_evidence_summary=self._summarize_weak_evidence({"reranked_chunks": evidence_chunks}),
                )
                self._record_tool(trace, "QueryRewriteTool", rewrite_output)
                current_query = rewrite_output["rewritten_query"]
                trace["rewritten_query"] = current_query
                retry_count += 1
                trace["retry_count"] = retry_count
                # Replacement strategy: after rewrite, use only rewritten-query
                # evidence. This keeps the final answer grounded in the query
                # that passed policy instead of mixing weak original evidence.
                continue

            refusal_output = self.tools.refusal.run(
                question=question,
                reason=policy_result.reason,
                best_scores=policy_result.stats.scores[:3],
            )
            self._record_tool(trace, "RefusalTool", refusal_output)
            trace["final_decision"] = "refuse"
            trace["final_answer"] = refusal_output
            break

        trace["completed_at"] = datetime.now(timezone.utc).isoformat()
        return trace

    def _run_evidence_loop(
        self,
        *,
        question: str,
        current_query: str,
        query_type: str,
        initial_evidence: list[dict[str, Any]],
        trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Detect evidence gaps and run one bounded round of follow-up retrieval."""
        gap = self.gap_detector.detect(question, initial_evidence, query_type)
        trace["evidence_gap_checks"].append(
            {
                "query": current_query,
                "has_gap": gap["has_gap"],
                "missing_fields": gap["missing_fields"],
                "followup_queries": gap["followup_queries"],
                "reason": gap["reason"],
            }
        )
        if gap["has_gap"]:
            trace["evidence_gap_detected"] = True
            trace["missing_fields"] = self._unique_strings([*trace["missing_fields"], *gap["missing_fields"]])
            trace["followup_queries"] = self._unique_strings([*trace["followup_queries"], *gap["followup_queries"]])

        merged_evidence = list(initial_evidence)
        if not gap["has_gap"]:
            trace["merged_evidence_count"] = len(merged_evidence)
            return {"has_gap": False, "merged_evidence": merged_evidence}

        for followup_query in gap["followup_queries"][: self.evidence_loop.max_followup_queries]:
            retrieval_output = self.tools.retrieval.run(
                query=followup_query,
                top_k=self.evidence_loop.followup_top_k,
                index_dir=self.index_dir,
            )
            self._record_tool(trace, "EvidenceFollowupRetrievalTool", retrieval_output)

            rerank_output = self.tools.rerank.run(
                query=followup_query,
                retrieved_chunks=retrieval_output["retrieved_chunks"],
                top_n=self.evidence_loop.followup_rerank_top_n,
            )
            self._record_tool(trace, "EvidenceFollowupRerankTool", rerank_output)
            trace["followup_tool_calls"].append(
                {
                    "query": followup_query,
                    "retrieval": retrieval_output,
                    "rerank": rerank_output,
                }
            )
            merged_evidence = self._merge_evidence(merged_evidence, rerank_output["reranked_chunks"])

        trace["merged_evidence_count"] = len(merged_evidence)
        return {"has_gap": True, "merged_evidence": merged_evidence}

    @staticmethod
    def _record_tool(trace: dict[str, Any], tool_name: str, output: dict[str, Any]) -> None:
        """Append a tool call record to the trace."""
        trace["tool_calls"].append(
            {
                "tool": tool_name,
                "output": output,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    @staticmethod
    def _record_policy(trace: dict[str, Any], result: PolicyResult, retry_count: int) -> None:
        """Append policy decision details to the trace."""
        trace["evidence_statistics"].append(
            {
                "decision": result.decision,
                "reason": result.reason,
                "retry_count": retry_count,
                "top_rerank_score": result.stats.top_rerank_score,
                "supporting_chunks": result.stats.supporting_chunks,
                "threshold": result.stats.threshold,
                "scores": result.stats.scores,
            }
        )

    def _merge_evidence(
        self,
        base_chunks: list[dict[str, Any]],
        followup_chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Append follow-up chunks while avoiding duplicate chunk IDs/text."""
        if self.evidence_loop.merge_strategy != "append_top_unique":
            raise ValueError(f"Unsupported evidence merge strategy: {self.evidence_loop.merge_strategy}")
        merged = list(base_chunks)
        seen = {self._chunk_key(chunk) for chunk in merged}
        for chunk in followup_chunks:
            key = self._chunk_key(chunk)
            if key in seen:
                continue
            merged.append(chunk)
            seen.add(key)
        return merged

    @staticmethod
    def _chunk_key(chunk: dict[str, Any]) -> str:
        metadata = chunk.get("metadata", {})
        return str(
            chunk.get("chunk_id")
            or (
                metadata.get("source_path"),
                metadata.get("file_name"),
                metadata.get("page_number"),
                chunk.get("text"),
            )
        )

    @staticmethod
    def _unique_strings(values: list[str]) -> list[str]:
        unique: list[str] = []
        for value in values:
            if value and value not in unique:
                unique.append(value)
        return unique

    @staticmethod
    def _summarize_weak_evidence(rerank_output: dict[str, Any]) -> str:
        """Create a small summary for query rewriting."""
        chunks = rerank_output.get("reranked_chunks", [])[:3]
        sections = [
            str(chunk.get("metadata", {}).get("section_title") or "unknown section")
            for chunk in chunks
        ]
        return f"Top weak sections: {', '.join(sections)}."
