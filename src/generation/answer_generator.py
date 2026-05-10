"""Naive RAG answer generation from retrieved chunks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.generation.llm_client import LLMClient
from src.prompts.rag_prompts import GROUNDED_QA_SYSTEM_PROMPT, GROUNDED_QA_USER_PROMPT


@dataclass(frozen=True)
class GeneratedAnswer:
    """Naive RAG answer payload."""

    question: str
    answer: str
    citations: list[dict[str, Any]]
    retrieved_chunks: list[dict[str, Any]]
    llm_mode: str
    llm_model: str


class AnswerGenerator:
    """Formats retrieval context and generates grounded answers."""

    def __init__(self, llm_client: LLMClient, *, max_context_chunks: int = 5) -> None:
        self.llm_client = llm_client
        self.max_context_chunks = max_context_chunks

    def generate(self, question: str, retrieved_chunks: list[dict[str, Any]]) -> GeneratedAnswer:
        """Generate an answer using the retrieved chunks as the only context."""
        context_chunks = retrieved_chunks[: self.max_context_chunks]
        context = self._format_context(context_chunks)
        user_prompt = GROUNDED_QA_USER_PROMPT.format(question=question, context=context)
        response = self.llm_client.chat(
            system_prompt=GROUNDED_QA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return GeneratedAnswer(
            question=question,
            answer=response.content.strip(),
            citations=self._citations_from_chunks(context_chunks),
            retrieved_chunks=context_chunks,
            llm_mode=response.mode,
            llm_model=response.model,
        )

    def _format_context(self, chunks: list[dict[str, Any]]) -> str:
        """Render chunks with source labels for grounded prompting."""
        parts = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            label = self._citation_label(index, chunk)
            source = metadata.get("file_name") or metadata.get("source_path") or "unknown source"
            page = metadata.get("page_number")
            section = metadata.get("section_title") or "unknown section"
            parts.append(
                f"{label}\n"
                f"source: {source}\n"
                f"page: {page}\n"
                f"section: {section}\n"
                f"score: {chunk.get('score')}\n"
                f"text: {chunk.get('text', '')}"
            )
        return "\n\n---\n\n".join(parts)

    def _citations_from_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Build citation records from retrieval metadata."""
        citations = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            citations.append(
                {
                    "label": self._citation_label(index, chunk),
                    "chunk_id": chunk.get("chunk_id"),
                    "source_path": metadata.get("source_path"),
                    "file_name": metadata.get("file_name"),
                    "page_number": metadata.get("page_number"),
                    "section_title": metadata.get("section_title"),
                    "score": chunk.get("score"),
                }
            )
        return citations

    @staticmethod
    def _citation_label(index: int, chunk: dict[str, Any]) -> str:
        """Create a compact citation label for a retrieved chunk."""
        chunk_id = str(chunk.get("chunk_id", ""))[:8] or f"rank-{index}"
        return f"[chunk:{index}:{chunk_id}]"

