"""Embedding utilities for indexing and retrieval.

The preferred embedder is `sentence-transformers` with the model configured in
`configs/default.yaml`. A deterministic hashing fallback is provided so local
development can still run when model downloads are unavailable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

import numpy as np


LOGGER = logging.getLogger(__name__)


class TextEmbedder(Protocol):
    """Common interface for text embedding backends."""

    model_name: str
    backend_name: str

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed a list of texts into a float32 matrix."""

    def embed_query(self, text: str) -> np.ndarray:
        """Embed one query into a float32 vector."""


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """L2-normalize rows for cosine similarity / inner product search."""
    matrix = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


@dataclass
class SentenceTransformersEmbedder:
    """Sentence-transformers embedder with normalized output."""

    model_name: str

    def __post_init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self.backend_name = "sentence-transformers"
        self._model = SentenceTransformer(self.model_name)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed documents with sentence-transformers."""
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a query with sentence-transformers."""
        return self.embed_texts([text])[0]


@dataclass
class HashingEmbedder:
    """Lightweight local fallback embedder based on hashed word features."""

    model_name: str
    n_features: int = 384

    def __post_init__(self) -> None:
        from sklearn.feature_extraction.text import HashingVectorizer

        self.backend_name = "hashing-fallback"
        self._vectorizer = HashingVectorizer(
            n_features=self.n_features,
            alternate_sign=False,
            norm=None,
            ngram_range=(1, 2),
        )

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed documents with deterministic hashing features."""
        matrix = self._vectorizer.transform(texts).astype(np.float32).toarray()
        return _normalize(matrix)

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a query with deterministic hashing features."""
        return self.embed_texts([text])[0]


def create_embedder(model_name: str, *, allow_fallback: bool = True) -> TextEmbedder:
    """Create the preferred embedder, falling back only when necessary."""
    try:
        embedder = SentenceTransformersEmbedder(model_name=model_name)
        LOGGER.info("Embedding model loaded: %s", model_name)
        return embedder
    except Exception as exc:
        if not allow_fallback:
            raise RuntimeError(f"Failed to load embedding model `{model_name}`: {exc}") from exc
        LOGGER.warning(
            "Falling back to local hashing embeddings because `%s` could not be loaded: %s",
            model_name,
            exc,
        )
        return HashingEmbedder(model_name=f"{model_name} (hashing fallback)")

