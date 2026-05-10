"""Compatibility wrapper for the preferred FAISS vector index backend.

The concrete builder lives in `src.indexing.vector_index` so the public indexing
flow can transparently fall back to NumPy when FAISS is unavailable.
"""

from src.indexing.vector_index import VectorIndexBuilder, VectorIndexInfo, build_vector_index

__all__ = ["VectorIndexBuilder", "VectorIndexInfo", "build_vector_index"]

