"""FAISS vector-store indexing boundary.

TODO:
- Wrap LangChain FAISS vector store.
- Persist embeddings and metadata.
- Support incremental updates and reindexing.
"""

from src.schemas import Chunk


class FaissIndexer:
    """Builds and persists a FAISS-backed vector index."""

    def index(self, chunks: list[Chunk]) -> None:
        """Index chunks into the configured FAISS store."""
        raise NotImplementedError

