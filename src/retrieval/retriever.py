"""Vector retriever with FAISS preferred and NumPy fallback."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from src.indexing.embedder import TextEmbedder, create_embedder
from src.indexing.vector_index import BACKEND_FILE, CHUNKS_FILE, EMBEDDINGS_FILE, FAISS_FILE
from src.schemas import Chunk


LOGGER = logging.getLogger(__name__)


def _load_chunks(path: Path) -> list[Chunk]:
    """Load persisted chunk mapping for retrieval."""
    chunks: list[Chunk] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                chunks.append(Chunk.model_validate_json(stripped))
    return chunks


class Retriever:
    """Load a persisted vector index and retrieve matching chunks."""

    def __init__(
        self,
        *,
        index_dir: Path,
        backend_info: dict[str, Any],
        chunks: list[Chunk],
        embeddings: np.ndarray,
        embedder: TextEmbedder,
        faiss_index: Any = None,
    ) -> None:
        self.index_dir = index_dir
        self.backend_info = backend_info
        self.backend = str(backend_info["backend"])
        self.chunks = chunks
        self.embeddings = embeddings.astype(np.float32)
        self.embedder = embedder
        self.faiss_index = faiss_index

    @classmethod
    def load(cls, index_dir: str | Path, *, embedding_model: str | None = None) -> "Retriever":
        """Load a persisted vector index from disk."""
        path = Path(index_dir)
        if not path.exists():
            raise FileNotFoundError(f"Index directory not found: {path}")

        backend_path = path / BACKEND_FILE
        chunks_path = path / CHUNKS_FILE
        embeddings_path = path / EMBEDDINGS_FILE
        for required_path in (backend_path, chunks_path, embeddings_path):
            if not required_path.exists():
                raise FileNotFoundError(f"Missing vector index artifact: {required_path}")

        backend_info = json.loads(backend_path.read_text(encoding="utf-8"))
        model_name = embedding_model or backend_info["embedding_model"]
        embedder = create_embedder(model_name)
        chunks = _load_chunks(chunks_path)
        embeddings = np.load(embeddings_path)

        faiss_index = None
        backend = backend_info.get("backend")
        if backend == "faiss":
            try:
                import faiss

                faiss_index = faiss.read_index(str(path / FAISS_FILE))
            except Exception as exc:
                LOGGER.warning("FAISS index could not be loaded; using NumPy fallback: %s", exc)
                backend_info = {**backend_info, "backend": "numpy"}

        LOGGER.info("Loaded vector index from: %s", path)
        LOGGER.info("Backend used: %s", backend_info["backend"])
        LOGGER.info("Embedding model: %s", model_name)
        return cls(
            index_dir=path,
            backend_info=backend_info,
            chunks=chunks,
            embeddings=embeddings,
            embedder=embedder,
            faiss_index=faiss_index,
        )

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve top-k chunks for a query.

        Returns dictionaries with `chunk_id`, `text`, `metadata`, and `score`.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_embedding = self.embedder.embed_query(query).astype(np.float32)
        k = min(top_k, len(self.chunks))

        if self.backend_info["backend"] == "faiss" and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query_embedding.reshape(1, -1), k)
            pairs = [(int(index), float(score)) for index, score in zip(indices[0], scores[0])]
        else:
            scores = self.embeddings @ query_embedding
            top_indices = np.argsort(scores)[::-1][:k]
            pairs = [(int(index), float(scores[index])) for index in top_indices]

        results = []
        for index, score in pairs:
            if index < 0:
                continue
            chunk = self.chunks[index]
            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "metadata": chunk.metadata,
                    "score": round(score, 6),
                }
            )
        return results


class EnterpriseRetriever(Retriever):
    """Backward-compatible name for the project retriever."""

