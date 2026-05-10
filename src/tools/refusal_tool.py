"""Insufficient-evidence refusal tool."""

from __future__ import annotations

from typing import Any

from src.tools.base import make_langchain_tool


class RefusalTool:
    """Create a grounded insufficient-evidence response."""

    name = "refuse_insufficient_evidence"
    description = "Return an insufficient-evidence response when retrieved context is weak."

    def run(
        self,
        *,
        question: str,
        reason: str,
        best_scores: list[float] | None = None,
    ) -> dict[str, Any]:
        """Return a structured refusal."""
        scores = best_scores or []
        score_text = f" Best available scores: {scores}." if scores else ""
        clean_reason = reason.rstrip(".!?")
        return {
            "question": question,
            "answer": (
                "I don't have enough grounded evidence to answer this question from the "
                f"available documents. Reason: {clean_reason}.{score_text}"
            ),
            "reason": reason,
            "best_scores": scores,
            "citations": [],
            "is_refusal": True,
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)
