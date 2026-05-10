"""Structured answer generation.

TODO:
- Use LangChain structured output with the `Answer` schema.
- Ground every answer in retrieved evidence.
- Produce concise reasoning summaries, not hidden chain-of-thought.
"""

from src.schemas import Answer, RetrievalResult


class StructuredAnswerGenerator:
    """Generates typed answers from validated evidence."""

    def generate(self, question: str, evidence: list[RetrievalResult]) -> Answer:
        """Generate a structured answer from evidence."""
        raise NotImplementedError

