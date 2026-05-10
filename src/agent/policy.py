"""Threshold-based evidence policy for the Agentic RAG executor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from src.agent.planner import QueryType


PolicyDecision = Literal["answer", "rewrite_and_retry", "refuse"]


@dataclass(frozen=True)
class EvidenceStats:
    """Evidence quality summary used for policy decisions."""

    top_rerank_score: float
    supporting_chunks: int
    threshold: float
    scores: list[float]


@dataclass(frozen=True)
class PolicyResult:
    """Decision emitted by evidence policy."""

    decision: PolicyDecision
    reason: str
    stats: EvidenceStats


@dataclass(frozen=True)
class EvidencePolicyConfig:
    """Configurable thresholds for evidence-aware decisions."""

    min_top_rerank_score: float = 0.5
    min_supporting_chunks: int = 1
    max_retries: int = 1
    weak_evidence_margin: float = 0.1


class EvidencePolicy:
    """Decide whether to answer, rewrite, or refuse based on evidence scores."""

    def __init__(self, config: EvidencePolicyConfig) -> None:
        self.config = config

    def evaluate(
        self,
        *,
        query_type: QueryType,
        reranked_chunks: list[dict[str, Any]],
        retry_count: int,
    ) -> PolicyResult:
        """Evaluate evidence quality and return an explicit decision."""
        stats = self._stats(query_type, reranked_chunks)
        has_enough_evidence = (
            stats.top_rerank_score >= stats.threshold
            and stats.supporting_chunks >= self._required_support(query_type)
        )

        if has_enough_evidence:
            return PolicyResult("answer", "Evidence meets configured support thresholds.", stats)

        if query_type == "ood_or_unanswerable" and self._is_weak(stats):
            return PolicyResult("refuse", "Query appears out of scope and retrieved evidence is weak.", stats)

        if retry_count < self.config.max_retries:
            return PolicyResult("rewrite_and_retry", "Evidence is weak; retry with a rewritten query.", stats)

        return PolicyResult("refuse", "Evidence remains insufficient after allowed retries.", stats)

    def _stats(self, query_type: QueryType, chunks: list[dict[str, Any]]) -> EvidenceStats:
        """Calculate score summary for reranked chunks."""
        threshold = self._threshold(query_type)
        scores = [float(chunk.get("rerank_score", chunk.get("score", 0.0))) for chunk in chunks]
        top = max(scores) if scores else 0.0
        supporting = sum(1 for score in scores if score >= threshold)
        return EvidenceStats(
            top_rerank_score=top,
            supporting_chunks=supporting,
            threshold=threshold,
            scores=scores,
        )

    def _threshold(self, query_type: QueryType) -> float:
        """Adjust threshold by query type."""
        if query_type in {"comparison", "multi_hop"}:
            return max(0.0, self.config.min_top_rerank_score - self.config.weak_evidence_margin)
        return self.config.min_top_rerank_score

    def _required_support(self, query_type: QueryType) -> int:
        """Require more supporting chunks for complex questions."""
        if query_type in {"comparison", "multi_hop"}:
            return self.config.min_supporting_chunks + 1
        return self.config.min_supporting_chunks

    def _is_weak(self, stats: EvidenceStats) -> bool:
        """Return whether evidence is materially below the answer threshold."""
        return stats.top_rerank_score < max(0.0, stats.threshold - self.config.weak_evidence_margin)

