"""Transparent lexical metrics for smoke-test RAG evaluation."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


REFUSAL_MARKERS = (
    "i don't know",
    "not enough grounded evidence",
    "insufficient evidence",
    "available documents",
    "provided context",
)


def normalize_text(text: object) -> str:
    """Normalize text for exact match and token metrics."""
    lowered = str(text or "").lower()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def tokenize(text: object) -> list[str]:
    """Tokenize normalized text."""
    return normalize_text(text).split()


def exact_match(predicted: object, expected: object) -> float:
    """Return normalized exact match."""
    return 1.0 if normalize_text(predicted) == normalize_text(expected) else 0.0


def token_f1(predicted: object, expected: object) -> float:
    """Return token-level F1."""
    pred_tokens = tokenize(predicted)
    gold_tokens = tokenize(expected)
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gold_tokens)
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def is_refusal(answer: object, decision: str | None = None) -> bool:
    """Detect refusal-style answers."""
    if decision == "refuse":
        return True
    normalized = normalize_text(answer)
    return any(normalize_text(marker) in normalized for marker in REFUSAL_MARKERS)


def retrieval_hit_at_k(chunks: list[dict[str, Any]], keywords: list[str], k: int) -> float:
    """Return 1 when any gold evidence keyword appears in top-k retrieved text."""
    if not keywords:
        return 0.0
    joined = " ".join(str(chunk.get("text", "")) for chunk in chunks[:k]).lower()
    return 1.0 if any(keyword.lower() in joined for keyword in keywords) else 0.0


def keyword_alignment(answer: object, chunks: list[dict[str, Any]], keywords: list[str]) -> float:
    """Measure whether answer or used evidence aligns with any gold keyword."""
    if not keywords:
        return 0.0
    answer_text = str(answer or "").lower()
    evidence_text = " ".join(str(chunk.get("text", "")) for chunk in chunks).lower()
    return 1.0 if any(keyword.lower() in answer_text or keyword.lower() in evidence_text for keyword in keywords) else 0.0


def unsupported_answer_proxy(answer: object, chunks: list[dict[str, Any]], keywords: list[str], decision: str | None) -> float:
    """Flag non-refusal answers that do not align with gold evidence keywords."""
    if is_refusal(answer, decision):
        return 0.0
    return 0.0 if keyword_alignment(answer, chunks, keywords) else 1.0


def mean(values: list[float]) -> float:
    """Safe arithmetic mean."""
    return sum(values) / len(values) if values else 0.0
