"""Explicit evidence-aware Agentic RAG executor.

This module intentionally avoids hiding the workflow inside a black-box
LangChain AgentExecutor. The sequence is readable and traceable:
plan -> retrieve -> rerank -> policy -> optional rewrite retry -> answer/refuse.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

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
    ) -> None:
        self.planner = planner
        self.policy = policy
        self.tools = tools
        self.index_dir = index_dir
        self.initial_top_k = initial_top_k
        self.rerank_top_n = rerank_top_n

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

            policy_result = self.policy.evaluate(
                query_type=plan.query_type,
                reranked_chunks=rerank_output["reranked_chunks"],
                retry_count=retry_count,
            )
            self._record_policy(trace, policy_result, retry_count)

            if policy_result.decision == "answer":
                answer_output = self.tools.answer.run(
                    question=question,
                    evidence_chunks=rerank_output["reranked_chunks"],
                )
                self._record_tool(trace, "AnswerTool", answer_output)
                trace["final_decision"] = "answer"
                trace["final_answer"] = answer_output
                break

            if policy_result.decision == "rewrite_and_retry":
                rewrite_output = self.tools.rewrite.run(
                    original_query=current_query,
                    reason=policy_result.reason,
                    failed_evidence_summary=self._summarize_weak_evidence(rerank_output),
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

    @staticmethod
    def _summarize_weak_evidence(rerank_output: dict[str, Any]) -> str:
        """Create a small summary for query rewriting."""
        chunks = rerank_output.get("reranked_chunks", [])[:3]
        sections = [
            str(chunk.get("metadata", {}).get("section_title") or "unknown section")
            for chunk in chunks
        ]
        return f"Top weak sections: {', '.join(sections)}."

