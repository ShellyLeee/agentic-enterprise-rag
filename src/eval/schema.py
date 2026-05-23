"""Shared benchmark example schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QAExample:
    """One question-answering benchmark example.

    ``documents`` stores candidate context for per-example retrieval. Each
    document should contain at least ``title``, ``text``, and ``source``.
    ``gold_evidence`` stores evidence hints used to evaluate retrieval.
    """

    id: str
    question: str
    answers: list[str]
    documents: list[dict[str, Any]] | None = None
    gold_evidence: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
