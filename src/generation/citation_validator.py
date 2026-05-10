"""Citation validation for generated answers.

TODO:
- Check that every citation maps to retrieved evidence.
- Verify cited text supports answer claims.
- Mark unsupported or partial answers before returning them.
"""

from src.schemas import Answer, RetrievalResult


class CitationValidator:
    """Validates whether cited evidence supports an answer."""

    def validate(self, answer: Answer, evidence: list[RetrievalResult]) -> Answer:
        """Return an answer with citation validation status updated."""
        return answer

