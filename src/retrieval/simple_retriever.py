"""Simple per-example TF-IDF retriever for benchmark fallback runs."""

from __future__ import annotations

from typing import Any


class SimpleRetriever:
    """Index in-memory documents and retrieve top-k by TF-IDF cosine score."""

    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self._vectorizer: Any | None = None
        self._matrix: Any | None = None

    def index(self, documents: list[dict[str, Any]]) -> None:
        """Build a TF-IDF index over ``documents``."""
        self.documents = documents
        if not documents:
            self._vectorizer = None
            self._matrix = None
            return
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError as exc:
            raise RuntimeError(
                "SimpleRetriever requires scikit-learn. Install dependencies with "
                "`pip install -r requirements.txt`."
            ) from exc

        texts = [str(document.get("text", "")) for document in documents]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        try:
            self._matrix = self._vectorizer.fit_transform(texts)
        except ValueError:
            self._vectorizer = TfidfVectorizer()
            try:
                self._matrix = self._vectorizer.fit_transform(texts)
            except ValueError:
                self._vectorizer = None
                self._matrix = None

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return top-k documents with a ``score`` field."""
        if not self.documents or self._vectorizer is None or self._matrix is None:
            return []
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")
        query_vector = self._vectorizer.transform([query])
        scores = (self._matrix @ query_vector.T).toarray().ravel()
        ranked_indices = scores.argsort()[::-1][: min(top_k, len(self.documents))]
        results = []
        for rank, index in enumerate(ranked_indices, start=1):
            document = dict(self.documents[int(index)])
            document.setdefault("chunk_id", f"doc-{int(index)}")
            document["score"] = round(float(scores[int(index)]), 6)
            document["rank"] = rank
            results.append(document)
        return results
