"""Retrieval tool wrapper for the agentic workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.retrieval.retriever import Retriever
from src.tools.base import make_langchain_tool


class RetrievalTool:
    """Direct Python-callable retrieval tool."""

    name = "retrieve_evidence"
    description = "Retrieve evidence chunks from the vector index."

    def __init__(self, *, embedding_model: str, retriever: Retriever | None = None) -> None:
        self.embedding_model = embedding_model
        self.retriever = retriever

    def run(self, *, query: str, top_k: int, index_dir: str | Path) -> dict[str, Any]:
        """Retrieve chunks for a query."""
        retriever = self.retriever or Retriever.load(Path(index_dir), embedding_model=self.embedding_model)
        chunks = retriever.retrieve(query, top_k=top_k)
        return {
            "query": query,
            "retrieved_chunks": chunks,
            "backend": retriever.backend_info.get("backend"),
            "embedding_model": self.embedding_model,
            "index_dir": str(index_dir),
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)
