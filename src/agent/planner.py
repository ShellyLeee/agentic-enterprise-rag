"""Explicit planning for the evidence-aware Agentic RAG workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


QueryType = Literal["simple", "comparison", "multi_hop", "ood_or_unanswerable"]


@dataclass(frozen=True)
class AgentPlan:
    """Lightweight plan metadata used by the executor and trace."""

    question: str
    query_type: QueryType
    steps: list[str]
    rationale: str


class AgentPlanner:
    """Classify the question and create an explicit tool-use plan."""

    def classify(self, question: str) -> QueryType:
        """Classify a query into the workflow types supported by the agent."""
        normalized = question.lower()
        if self._looks_ood(normalized):
            return "ood_or_unanswerable"
        if re.search(r"\b(compare|versus|vs\.?|higher|lower|lowest|highest|difference|which)\b", normalized):
            return "comparison"
        if re.search(r"\b(and|across|between|relationship|both|several|multiple)\b", normalized):
            return "multi_hop"
        return "simple"

    def plan(self, question: str) -> AgentPlan:
        """Return an explicit high-level plan for a question."""
        query_type = self.classify(question)
        steps = ["retrieve", "rerank", "policy_decision"]
        if query_type in {"comparison", "multi_hop"}:
            steps.append("require_more_supporting_evidence")
        steps.extend(["answer_or_rewrite_or_refuse", "trace"])
        return AgentPlan(
            question=question,
            query_type=query_type,
            steps=steps,
            rationale=f"Question classified as {query_type}; use evidence thresholds before answering.",
        )

    @staticmethod
    def _looks_ood(normalized_question: str) -> bool:
        """Detect clearly unsupported HR/benefit topics for this early sample corpus."""
        ood_phrases = {
            "pet insurance",
            "parental leave",
            "health insurance",
            "401k",
            "tuition reimbursement",
            "stock options",
        }
        return any(phrase in normalized_question for phrase in ood_phrases)

