"""Parent-document expansion for retrieved chunks.

TODO:
- Expand chunk hits to page-level or section-level parent context.
- Avoid duplicating parent pages across retrieval results.
"""

from src.schemas import RetrievalResult


class ParentDocumentExpander:
    """Attaches parent page or section context to retrieval results."""

    def expand(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        """Attach parent document context to each retrieval result."""
        return results

