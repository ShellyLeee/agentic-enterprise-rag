"""Vector index persistence with FAISS preferred and NumPy fallback."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.indexing.embedder import TextEmbedder, create_embedder
from src.schemas import Chunk


LOGGER = logging.getLogger(__name__)
EMBEDDINGS_FILE = "embeddings.npy"
CHUNKS_FILE = "chunks.jsonl"
BACKEND_FILE = "backend.json"
FAISS_FILE = "index.faiss"


@dataclass(frozen=True)
class VectorIndexInfo:
    """Metadata about a persisted vector index."""

    backend: str
    index_dir: Path
    embedding_model: str
    embedding_backend: str
    chunk_count: int


def load_chunks_jsonl(path: str | Path) -> list[Chunk]:
    """Load canonical chunks from a JSONL file."""
    chunk_path = Path(path)
    if not chunk_path.exists():
        raise FileNotFoundError(f"Chunks JSONL file not found: {chunk_path}")

    chunks: list[Chunk] = []
    with chunk_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                chunks.append(Chunk.model_validate_json(stripped))
            except Exception as exc:
                raise ValueError(f"Invalid chunk JSON on line {line_number} of {chunk_path}: {exc}") from exc
    if not chunks:
        raise ValueError(f"No chunks found in {chunk_path}")
    return chunks


def _write_chunks(path: Path, chunks: list[Chunk]) -> None:
    """Persist chunk mapping beside the vector index."""
    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk.model_dump(mode="json"), ensure_ascii=False) + "\n")


def _try_build_faiss(embeddings: np.ndarray, output_path: Path) -> str | None:
    """Persist a FAISS index if FAISS is installed."""
    try:
        import faiss
    except Exception:
        return None

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    faiss.write_index(index, str(output_path))
    return "faiss"


class VectorIndexBuilder:
    """Build and persist a vector index from chunk JSONL."""

    def __init__(self, embedder: TextEmbedder) -> None:
        self.embedder = embedder

    def build(self, chunks: list[Chunk], index_dir: str | Path) -> VectorIndexInfo:
        """Embed chunks and persist index artifacts."""
        output_dir = Path(index_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts).astype(np.float32)
        np.save(output_dir / EMBEDDINGS_FILE, embeddings)
        _write_chunks(output_dir / CHUNKS_FILE, chunks)

        backend = _try_build_faiss(embeddings, output_dir / FAISS_FILE) or "numpy"
        backend_info: dict[str, Any] = {
            "backend": backend,
            "embedding_model": self.embedder.model_name,
            "embedding_backend": self.embedder.backend_name,
            "chunk_count": len(chunks),
            "dimension": int(embeddings.shape[1]),
        }
        (output_dir / BACKEND_FILE).write_text(
            json.dumps(backend_info, indent=2),
            encoding="utf-8",
        )

        LOGGER.info("Embedding model: %s", self.embedder.model_name)
        LOGGER.info("Chunks indexed: %s", len(chunks))
        LOGGER.info("Backend used: %s", backend)
        LOGGER.info("Index output path: %s", output_dir)

        return VectorIndexInfo(
            backend=backend,
            index_dir=output_dir,
            embedding_model=self.embedder.model_name,
            embedding_backend=self.embedder.backend_name,
            chunk_count=len(chunks),
        )


def build_vector_index(
    *,
    chunks_path: str | Path,
    index_dir: str | Path,
    embedding_model: str,
) -> VectorIndexInfo:
    """Load chunks, create embeddings, and persist a vector index."""
    chunks = load_chunks_jsonl(chunks_path)
    embedder = create_embedder(embedding_model)
    return VectorIndexBuilder(embedder).build(chunks, index_dir)

