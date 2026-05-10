"""Retrieval tools for agent use.

TODO:
- Wrap retrievers as LangChain tools.
- Add tool schemas for document lookup, table lookup, and citation lookup.
"""

from src.schemas import RetrievalResult


def retrieve_evidence(question: str) -> list[RetrievalResult]:
    """Retrieve evidence for a question.

    Placeholder for a future LangChain tool implementation.
    """
    raise NotImplementedError

