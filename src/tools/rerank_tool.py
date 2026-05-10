"""Reranking tool wrapper for the agentic workflow."""

from __future__ import annotations

from typing import Any

from src.retrieval.reranker import Reranker
from src.tools.base import make_langchain_tool


class RerankTool:
    """Direct Python-callable reranking tool."""

    name = "rerank_evidence"
    description = "Rerank retrieved evidence chunks for a query."

    def __init__(self, *, model_name: str, backend: str = "auto", fallback: bool = True) -> None:
        self.model_name = model_name
        self.backend = backend
        self.fallback = fallback

    def run(
        self,
        *,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
        top_n: int,
    ) -> dict[str, Any]:
        """Rerank retrieved chunks."""
        reranker = Reranker(model_name=self.model_name, backend=self.backend, fallback=self.fallback)
        reranked = reranker.rerank(query, retrieved_chunks, top_n=top_n)
        return {
            "query": query,
            "reranked_chunks": reranked,
            "reranker_backend": reranker.backend_used,
            "reranker_model": self.model_name,
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)

