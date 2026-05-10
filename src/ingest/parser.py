"""Parser adapter interfaces for raw enterprise documents.

TODO:
- Add Docling-backed PDF parser adapter.
- Normalize parser-specific output into `src.schemas.Document`.
- Preserve immutable raw parse artifacts separately from processed documents.
"""

from src.schemas import Document


class DocumentParser:
    """Abstract parser boundary for source documents."""

    def parse(self, source_uri: str) -> Document:
        """Parse a source document into the canonical document schema."""
        raise NotImplementedError

