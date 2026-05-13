"""Threshold-based evidence policy for the Agentic RAG executor."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from src.agent.planner import QueryType


PolicyDecision = Literal["answer", "rewrite_and_retry", "refuse"]
ScoreMode = Literal["rerank_only", "retrieval_only", "hybrid"]


@dataclass(frozen=True)
class EvidenceStats:
    """Evidence quality summary used for policy decisions."""

    top_rerank_score: float
    top_retrieval_score: float
    supporting_chunks: int
    threshold: float
    rerank_threshold: float
    retrieval_threshold: float
    scores: list[float]
    rerank_scores: list[float]
    retrieval_scores: list[float]
    num_chunks_above_rerank_threshold: int
    num_chunks_above_retrieval_threshold: int
    lexical_match_terms: list[str]
    has_strong_lexical_match: bool
    score_mode: ScoreMode


@dataclass(frozen=True)
class PolicyResult:
    """Decision emitted by evidence policy."""

    decision: PolicyDecision
    reason: str
    stats: EvidenceStats


@dataclass(frozen=True)
class EvidencePolicyConfig:
    """Configurable thresholds for evidence-aware decisions."""

    score_mode: ScoreMode = "hybrid"
    min_top_retrieval_score: float = 0.65
    min_top_rerank_score: float = 0.005
    min_supporting_chunks: int = 1
    max_retries: int = 1
    weak_evidence_margin: float = 0.1


class EvidencePolicy:
    """Decide whether to answer, rewrite, or refuse based on evidence scores."""

    def __init__(self, config: EvidencePolicyConfig) -> None:
        if config.score_mode not in {"rerank_only", "retrieval_only", "hybrid"}:
            raise ValueError(f"Unsupported evidence score_mode: {config.score_mode}")
        self.config = config

    def evaluate(
        self,
        *,
        query_type: QueryType,
        reranked_chunks: list[dict[str, Any]],
        retry_count: int,
        question: str = "",
    ) -> PolicyResult:
        """Evaluate evidence quality and return an explicit decision."""
        stats = self._stats(query_type, reranked_chunks, question)
        has_enough_evidence = self._has_enough_evidence(stats)

        if has_enough_evidence:
            return PolicyResult("answer", "Evidence meets configured hybrid support thresholds.", stats)

        if query_type == "ood_or_unanswerable" and self._is_weak(stats):
            return PolicyResult("refuse", "Query appears out of scope and retrieved evidence is weak.", stats)

        if retry_count < self.config.max_retries:
            return PolicyResult("rewrite_and_retry", "Evidence is weak; retry with a rewritten query.", stats)

        return PolicyResult("refuse", "Evidence remains insufficient after allowed retries.", stats)

    def _stats(self, query_type: QueryType, chunks: list[dict[str, Any]], question: str) -> EvidenceStats:
        """Calculate score summary for reranked chunks."""
        rerank_threshold = self._rerank_threshold(query_type)
        retrieval_threshold = self._retrieval_threshold(query_type)
        rerank_scores = [float(chunk.get("rerank_score", chunk.get("score", 0.0)) or 0.0) for chunk in chunks]
        retrieval_scores = [float(chunk.get("retrieval_score", chunk.get("score", 0.0)) or 0.0) for chunk in chunks]
        top_rerank = max(rerank_scores) if rerank_scores else 0.0
        top_retrieval = max(retrieval_scores) if retrieval_scores else 0.0
        above_rerank = sum(1 for score in rerank_scores if score >= rerank_threshold)
        above_retrieval = sum(1 for score in retrieval_scores if score >= retrieval_threshold)
        lexical_match_terms = self._lexical_match_terms(question, chunks)
        has_strong_lexical_match = self._has_strong_lexical_match(question, lexical_match_terms)
        supporting = max(
            above_rerank if self.config.score_mode in {"rerank_only", "hybrid"} else 0,
            above_retrieval if self.config.score_mode in {"retrieval_only", "hybrid"} and has_strong_lexical_match else 0,
        )
        return EvidenceStats(
            top_rerank_score=top_rerank,
            top_retrieval_score=top_retrieval,
            supporting_chunks=supporting,
            threshold=rerank_threshold,
            rerank_threshold=rerank_threshold,
            retrieval_threshold=retrieval_threshold,
            scores=rerank_scores,
            rerank_scores=rerank_scores,
            retrieval_scores=retrieval_scores,
            num_chunks_above_rerank_threshold=above_rerank,
            num_chunks_above_retrieval_threshold=above_retrieval,
            lexical_match_terms=lexical_match_terms,
            has_strong_lexical_match=has_strong_lexical_match,
            score_mode=self.config.score_mode,
        )

    def _rerank_threshold(self, query_type: QueryType) -> float:
        """Adjust threshold by query type."""
        return self.config.min_top_rerank_score

    def _retrieval_threshold(self, query_type: QueryType) -> float:
        """Adjust retrieval threshold by query type."""
        return self.config.min_top_retrieval_score

    def _has_enough_evidence(self, stats: EvidenceStats) -> bool:
        """Return whether either configured score path supports answering."""
        required_support = self._required_support()
        rerank_ok = stats.top_rerank_score >= stats.rerank_threshold
        retrieval_ok = (
            stats.top_retrieval_score >= stats.retrieval_threshold
            and stats.has_strong_lexical_match
        )

        if self.config.score_mode == "rerank_only":
            score_ok = rerank_ok
        elif self.config.score_mode == "retrieval_only":
            score_ok = retrieval_ok
        else:
            score_ok = rerank_ok or retrieval_ok
        return score_ok and stats.supporting_chunks >= required_support

    def _required_support(self) -> int:
        """Require more supporting chunks for complex questions."""
        return self.config.min_supporting_chunks

    def _is_weak(self, stats: EvidenceStats) -> bool:
        """Return whether evidence is materially below the answer threshold."""
        weak_rerank = stats.top_rerank_score < self._weak_cutoff(stats.rerank_threshold)
        weak_retrieval = stats.top_retrieval_score < self._weak_cutoff(stats.retrieval_threshold)
        return weak_rerank and weak_retrieval

    def _weak_cutoff(self, threshold: float) -> float:
        """Apply weak margin without erasing tiny real-reranker thresholds."""
        margin = min(self.config.weak_evidence_margin, threshold * 0.5)
        return max(0.0, threshold - margin)

    def _lexical_match_terms(self, question: str, chunks: list[dict[str, Any]]) -> list[str]:
        """Return important question/domain terms present in retrieved evidence."""
        evidence_text = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
        question_terms = self._question_terms(question)
        matches = [term for term in question_terms if term in evidence_text]
        for question_phrase, evidence_terms in self._domain_equivalents().items():
            if question_phrase in question.lower() and any(term in evidence_text for term in evidence_terms):
                matches.append(question_phrase)
        unique: list[str] = []
        for term in matches:
            if term not in unique:
                unique.append(term)
        return unique

    @staticmethod
    def _question_terms(question: str) -> list[str]:
        stopwords = {
            "a",
            "an",
            "and",
            "any",
            "company",
            "companies",
            "did",
            "does",
            "for",
            "from",
            "in",
            "is",
            "of",
            "or",
            "the",
            "this",
            "to",
            "was",
            "what",
            "which",
            "who",
        }
        return [
            token
            for token in re.findall(r"[a-z0-9]+", question.lower())
            if len(token) > 2 and token not in stopwords
        ]

    @staticmethod
    def _domain_equivalents() -> dict[str, tuple[str, ...]]:
        return {
            "buyback": ("repurchase", "share repurchase", "stock repurchase"),
            "share buyback": ("share repurchase", "repurchase program", "repurchase plan"),
            "mergers": ("business combination", "acquisition", "acquisitions", "merger"),
            "acquisitions": ("business combination", "acquisition", "merger", "mergers"),
            "operating margin": ("operating margin", "adjusted operating margin", "reported operating margin"),
        }

    @staticmethod
    def _has_strong_lexical_match(question: str, match_terms: list[str]) -> bool:
        if not question.strip():
            return False
        return len(match_terms) >= 2 or any(" " in term for term in match_terms)
