"""Token-aware chunking with parent-page preservation.

TODO:
- Use LangChain splitters to create chunks with stable IDs.
- Keep page, document, organization, and section metadata on every chunk.
"""

from src.schemas import Chunk, Document


class DocumentChunker:
    """Converts normalized documents into retrieval chunks."""

    def split(self, document: Document) -> list[Chunk]:
        """Split a document into chunks."""
        raise NotImplementedError

