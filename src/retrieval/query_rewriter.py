"""Query rewriting for retrieval-focused search prompts.

TODO:
- Rewrite user questions into search queries.
- Preserve original question intent and required entities.
- Return multiple query variants for broad and precise retrieval.
"""


class QueryRewriter:
    """Produces retrieval-ready query variants."""

    def rewrite(self, question: str) -> list[str]:
        """Return query variants for retrieval."""
        return [question]

