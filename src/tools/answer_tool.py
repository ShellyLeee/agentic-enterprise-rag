"""Answer generation tool wrapper for the agentic workflow."""

from __future__ import annotations

from typing import Any

from src.generation.answer_generator import AnswerGenerator
from src.tools.base import make_langchain_tool


class AnswerTool:
    """Direct Python-callable answer generation tool."""

    name = "answer_from_evidence"
    description = "Generate a grounded answer from evidence chunks."

    def __init__(self, generator: AnswerGenerator) -> None:
        self.generator = generator

    def run(self, *, question: str, evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate an answer from evidence chunks."""
        answer = self.generator.generate(question, evidence_chunks)
        return {
            "question": answer.question,
            "answer": answer.answer,
            "citations": answer.citations,
            "evidence_used": answer.retrieved_chunks,
            "llm_mode": answer.llm_mode,
            "llm_model": answer.llm_model,
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)

