"""Query rewrite tool for the agentic workflow."""

from __future__ import annotations

import re
from typing import Any

from src.generation.llm_client import LLMClient
from src.tools.base import make_langchain_tool


class QueryRewriteTool:
    """Rewrite vague or failed queries into retrieval-focused searches."""

    name = "rewrite_query"
    description = "Rewrite a user query for better retrieval."

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(
        self,
        *,
        original_query: str,
        reason: str | None = None,
        failed_evidence_summary: str | None = None,
    ) -> dict[str, Any]:
        """Rewrite a query, using deterministic mock logic when configured."""
        if self.llm_client.mock:
            rewritten = self._mock_rewrite(original_query, reason, failed_evidence_summary)
            mode = "mock"
        else:
            prompt = (
                "Rewrite the query for enterprise policy retrieval. Preserve the user's intent. "
                "Return only the rewritten query.\n\n"
                f"Original query: {original_query}\n"
                f"Reason: {reason or 'not provided'}\n"
                f"Failed evidence summary: {failed_evidence_summary or 'not provided'}"
            )
            response = self.llm_client.chat(
                system_prompt="You rewrite queries for retrieval. Return only the rewritten query.",
                user_prompt=prompt,
            )
            rewritten = response.content.strip().strip('"')
            mode = response.mode

        return {
            "original_query": original_query,
            "rewritten_query": rewritten,
            "reason": reason,
            "failed_evidence_summary": failed_evidence_summary,
            "mode": mode,
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)

    @staticmethod
    def _mock_rewrite(
        original_query: str,
        reason: str | None,
        failed_evidence_summary: str | None,
    ) -> str:
        """Produce deterministic, retrieval-focused mock rewrites."""
        query = re.sub(r"\s+", " ", original_query.strip())
        lower = query.lower()
        additions = []
        if "vacation" not in lower and any(term in lower for term in {"time off", "pto", "days"}):
            additions.append("vacation policy")
        if "remote" not in lower and "work from home" in lower:
            additions.append("remote work policy")
        if "expense" not in lower and any(term in lower for term in {"receipt", "reimburse", "travel"}):
            additions.append("expense reimbursement")
        if reason:
            additions.append(reason)
        if failed_evidence_summary:
            additions.append(failed_evidence_summary)
        if additions:
            return f"{query} {' '.join(additions)}"
        return f"{query} enterprise policy"

