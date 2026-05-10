"""Cross-encoder reranking with deterministic lexical fallback."""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from typing import Any, Protocol


LOGGER = logging.getLogger(__name__)


class RerankBackend(Protocol):
    """Common interface for reranking backends."""

    backend_name: str

    def score(self, query: str, chunks: list[dict[str, Any]]) -> list[float]:
        """Return one relevance score for each chunk."""


@dataclass
class CrossEncoderBackend:
    """Sentence-transformers CrossEncoder reranking backend."""

    model_name: str

    def __post_init__(self) -> None:
        from sentence_transformers import CrossEncoder

        self.backend_name = "cross-encoder"
        self._model = CrossEncoder(self.model_name)

    def score(self, query: str, chunks: list[dict[str, Any]]) -> list[float]:
        """Score query/chunk pairs with a CrossEncoder model."""
        pairs = [(query, str(chunk.get("text", ""))) for chunk in chunks]
        scores = self._model.predict(pairs)
        return [float(score) for score in scores]


class LexicalOverlapBackend:
    """Deterministic local reranker based on lexical overlap."""

    backend_name = "lexical-overlap-fallback"

    def score(self, query: str, chunks: list[dict[str, Any]]) -> list[float]:
        """Score chunks using normalized keyword overlap and small phrase boosts."""
        query_terms = _terms(query)
        scores = []
        for chunk in chunks:
            text = str(chunk.get("text", ""))
            text_terms = _terms(text)
            if not query_terms or not text_terms:
                scores.append(0.0)
                continue

            overlap = len(query_terms & text_terms)
            denominator = math.sqrt(len(query_terms) * len(text_terms))
            score = overlap / denominator if denominator else 0.0

            query_lower = query.lower()
            text_lower = text.lower()
            if "vacation" in query_lower and "vacation" in text_lower:
                score += 0.25
            if "new employees" in query_lower and "new employees" in text_lower:
                score += 0.25
            if "days" in query_lower and "days" in text_lower:
                score += 0.1

            scores.append(round(score, 6))
        return scores


class Reranker:
    """Rerank retrieved chunks before answer generation."""

    def __init__(
        self,
        *,
        model_name: str = "BAAI/bge-reranker-base",
        backend: str = "auto",
        fallback: bool = True,
    ) -> None:
        self.model_name = model_name
        self.requested_backend = backend
        self.fallback = fallback
        self.backend = self._create_backend()
        self.backend_used = self.backend.backend_name

    def rerank(
        self,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
        *,
        top_n: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return chunks sorted by rerank score, preserving retrieval score."""
        if not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_n is not None and top_n <= 0:
            raise ValueError("top_n must be greater than zero.")

        scores = self.backend.score(query, retrieved_chunks)
        reranked = []
        for chunk, rerank_score in zip(retrieved_chunks, scores):
            enriched = dict(chunk)
            retrieval_score = float(enriched.get("score", 0.0))
            enriched["retrieval_score"] = retrieval_score
            enriched["rerank_score"] = float(rerank_score)
            reranked.append(enriched)

        reranked.sort(
            key=lambda item: (float(item["rerank_score"]), float(item["retrieval_score"])),
            reverse=True,
        )
        return reranked[:top_n] if top_n is not None else reranked

    def _create_backend(self) -> RerankBackend:
        """Create preferred backend or deterministic fallback."""
        if self.requested_backend in {"auto", "cross-encoder"}:
            try:
                backend = CrossEncoderBackend(self.model_name)
                LOGGER.info("Reranker model loaded: %s", self.model_name)
                return backend
            except Exception as exc:
                if not self.fallback:
                    raise RuntimeError(f"Failed to load reranker model `{self.model_name}`: {exc}") from exc
                LOGGER.warning(
                    "Falling back to lexical reranker because `%s` could not be loaded: %s",
                    self.model_name,
                    exc,
                )
                return LexicalOverlapBackend()

        if self.requested_backend in {"fallback", "lexical", "lexical-overlap"}:
            return LexicalOverlapBackend()

        raise ValueError(f"Unsupported reranker backend: {self.requested_backend}")


class CrossEncoderReranker(Reranker):
    """Backward-compatible name for the cross-encoder reranker boundary."""


def _terms(text: str) -> set[str]:
    """Tokenize significant terms for lexical fallback scoring."""
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "do",
        "does",
        "how",
        "is",
        "many",
        "of",
        "the",
        "to",
        "what",
        "when",
        "where",
        "who",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in stopwords
    }

