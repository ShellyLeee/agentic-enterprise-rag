"""Transparent QA and retrieval metrics for benchmark runs."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Any


def normalize_answer(s: object) -> str:
    """Lowercase, remove punctuation/articles, and normalize whitespace."""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    return white_space_fix(remove_articles(remove_punc(str(s or "").lower())))


def exact_match_score(prediction: object, ground_truths: list[str]) -> float:
    """Return the best normalized exact-match score over all gold answers."""
    if not ground_truths:
        return 0.0
    normalized_prediction = normalize_answer(prediction)
    return max(1.0 if normalized_prediction == normalize_answer(answer) else 0.0 for answer in ground_truths)


def f1_score(prediction: object, ground_truths: list[str]) -> float:
    """Return the best token-level F1 score over all gold answers."""
    if not ground_truths:
        return 0.0
    return max(_f1_single(prediction, answer) for answer in ground_truths)


def retrieval_hit_at_k(
    retrieved_docs: list[dict[str, Any]],
    gold_evidence: list[dict[str, Any]] | None,
) -> float:
    """Return 1.0 when any gold title/text evidence appears in retrieved docs.

    This intentionally starts simple: a hit is counted if a gold title matches
    a retrieved title/source, or if a gold text substring appears in retrieved
    text. It works for HotpotQA supporting facts and loose FinanceBench samples.
    """
    if not retrieved_docs or not gold_evidence:
        return 0.0

    retrieved_titles = {
        normalize_answer(
            doc.get("title")
            or doc.get("doc_name")
            or doc.get("source")
            or doc.get("metadata", {}).get("title")
            or doc.get("metadata", {}).get("doc_name")
        )
        for doc in retrieved_docs
    }
    retrieved_text = normalize_answer("\n".join(str(doc.get("text", "")) for doc in retrieved_docs))

    for evidence in gold_evidence:
        title = normalize_answer(evidence.get("title") or evidence.get("doc_name") or evidence.get("source") or "")
        if title and title in retrieved_titles:
            return 1.0
        text = evidence.get("text") or evidence.get("sentence") or evidence.get("full_page_text") or ""
        if _partial_text_match(text, retrieved_text):
            return 1.0
    return 0.0


def _partial_text_match(gold_text: object, normalized_retrieved_text: str) -> bool:
    """Return true when normalized gold text substantially overlaps retrieved text."""
    normalized_gold = normalize_answer(gold_text)
    if not normalized_gold or not normalized_retrieved_text:
        return False
    if normalized_gold in normalized_retrieved_text:
        return True

    gold_tokens = normalized_gold.split()
    if len(gold_tokens) >= 12:
        for start in range(0, len(gold_tokens) - 11, 6):
            window = " ".join(gold_tokens[start : start + 12])
            if window in normalized_retrieved_text:
                return True

    retrieved_tokens = set(normalized_retrieved_text.split())
    if not retrieved_tokens or len(gold_tokens) < 4:
        return False
    overlap = sum(1 for token in gold_tokens if token in retrieved_tokens)
    return overlap / len(gold_tokens) >= 0.5


def _f1_single(prediction: object, ground_truth: object) -> float:
    """Compute token-level F1 for one prediction/gold pair."""
    prediction_tokens = normalize_answer(prediction).split()
    ground_truth_tokens = normalize_answer(ground_truth).split()
    if not prediction_tokens and not ground_truth_tokens:
        return 1.0
    if not prediction_tokens or not ground_truth_tokens:
        return 0.0
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(prediction_tokens)
    recall = num_same / len(ground_truth_tokens)
    return 2 * precision * recall / (precision + recall)
