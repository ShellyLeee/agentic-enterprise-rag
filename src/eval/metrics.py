"""Transparent QA and retrieval metrics for benchmark runs."""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Any

ABSTENTION_MARKERS = (
    "not sure",
    "insufficient context",
    "insufficient evidence",
    "cannot determine",
    "can't determine",
    "unknown",
    "not enough information",
    "not enough context",
    "provided context does not",
)


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


def numeric_match_score(
    prediction: object,
    ground_truths: list[str],
    tolerance: float = 0.02,
) -> float:
    """Return 1.0 when any predicted number matches a gold number within tolerance.

    The parser handles common FinanceBench formats such as dollars, commas,
    percentages, negative parentheses, and million/billion unit scaling.
    """
    prediction_numbers = _extract_numbers(prediction)
    if not prediction_numbers:
        return 0.0
    for answer in ground_truths:
        for gold_number in _extract_numbers(answer):
            for predicted_number in prediction_numbers:
                if _numbers_match(predicted_number, gold_number, tolerance):
                    return 1.0
    return 0.0


def boolean_accuracy_score(prediction: object, ground_truths: list[str]) -> float | None:
    """Return yes/no accuracy when the gold answer is boolean, otherwise None."""
    gold_labels = [_extract_boolean_label(answer) for answer in ground_truths]
    gold_labels = [label for label in gold_labels if label is not None]
    if not gold_labels:
        return None
    predicted = _extract_boolean_label(prediction, prefer_final=True)
    if predicted is None:
        return 0.0
    return 1.0 if predicted in gold_labels else 0.0


def detect_abstention(prediction: object) -> bool:
    """Detect answers that abstain because evidence or knowledge is insufficient."""
    normalized = normalize_answer(prediction)
    return any(normalize_answer(marker) in normalized for marker in ABSTENTION_MARKERS)


def hit_at_k(
    retrieved_docs: list[dict[str, Any]],
    gold_evidence: list[dict[str, Any]] | None,
    k: int | None = None,
) -> float:
    """Return 1.0 when any gold evidence item appears in top-k retrieved docs."""
    docs = retrieved_docs[:k] if k is not None else retrieved_docs
    return retrieval_hit_at_k(docs, gold_evidence)


def evidence_recall_at_k(
    retrieved_docs: list[dict[str, Any]],
    gold_evidence: list[dict[str, Any]] | None,
    k: int | None = None,
) -> float:
    """Return fraction of gold evidence items matched by the top-k retrieved docs."""
    if not gold_evidence:
        return 0.0
    docs = retrieved_docs[:k] if k is not None else retrieved_docs
    matched = sum(1 for evidence in gold_evidence if _any_doc_matches_evidence(docs, evidence))
    return matched / len(gold_evidence)


def mrr(
    retrieved_docs: list[dict[str, Any]],
    gold_evidence: list[dict[str, Any]] | None,
    k: int | None = None,
) -> float:
    """Return reciprocal rank of the first retrieved doc that matches gold evidence."""
    if not retrieved_docs or not gold_evidence:
        return 0.0
    docs = retrieved_docs[:k] if k is not None else retrieved_docs
    for rank, doc in enumerate(docs, start=1):
        if any(_doc_matches_evidence(doc, evidence) for evidence in gold_evidence):
            return 1.0 / rank
    return 0.0


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

    for evidence in gold_evidence:
        if _any_doc_matches_evidence(retrieved_docs, evidence):
            return 1.0
    return 0.0


def _any_doc_matches_evidence(docs: list[dict[str, Any]], evidence: dict[str, Any]) -> bool:
    """Return true when any retrieved doc matches one gold evidence record."""
    return any(_doc_matches_evidence(doc, evidence) for doc in docs)


def _doc_matches_evidence(doc: dict[str, Any], evidence: dict[str, Any]) -> bool:
    """Return true when one retrieved doc matches one evidence record."""
    doc_chunk_id = str(doc.get("chunk_id") or doc.get("id") or "")
    evidence_chunk_id = str(evidence.get("chunk_id") or "")
    if evidence_chunk_id and doc_chunk_id and evidence_chunk_id == doc_chunk_id:
        return True

    doc_title = normalize_answer(
        doc.get("title")
        or doc.get("doc_name")
        or doc.get("source_doc")
        or doc.get("source")
        or doc.get("metadata", {}).get("title")
        or doc.get("metadata", {}).get("doc_name")
        or doc.get("metadata", {}).get("file_name")
    )
    evidence_title = normalize_answer(
        evidence.get("title") or evidence.get("doc_name") or evidence.get("source_doc") or evidence.get("source") or ""
    )
    if evidence_title and doc_title and evidence_title == doc_title:
        return True

    doc_text = normalize_answer(doc.get("text") or doc.get("chunk_text") or "")
    evidence_text = (
        evidence.get("text")
        or evidence.get("evidence_text")
        or evidence.get("sentence")
        or evidence.get("full_page_text")
        or ""
    )
    return _partial_text_match(evidence_text, doc_text)


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


def _extract_numbers(text: object) -> list[float]:
    """Extract normalized numeric values with simple financial unit handling."""
    raw = str(text or "")
    pattern = re.compile(
        r"(?P<negative>\()?\s*(?:USD\s*)?\$?\s*"
        r"(?P<number>-?\d[\d,]*(?:\.\d+)?)\s*"
        r"(?P<unit>%|percent|percentage|million|millions|billion|billions|bn|mm)?\s*\)?",
        flags=re.IGNORECASE,
    )
    values = []
    for match in pattern.finditer(raw):
        number_text = match.group("number").replace(",", "")
        try:
            value = float(number_text)
        except ValueError:
            continue
        if match.group("negative") or _is_parenthesized_negative(raw, match.start(), match.end()):
            value = -abs(value)
        unit = (match.group("unit") or "").lower()
        value *= _unit_multiplier(unit, raw[max(0, match.start() - 20) : match.end() + 20])
        values.append(value)
    return values


def _unit_multiplier(unit: str, context: str) -> float:
    """Return a scale factor for simple finance units."""
    lowered = context.lower()
    if unit in {"million", "millions", "mm"} or "usd millions" in lowered or "in millions" in lowered:
        return 1_000_000.0
    if unit in {"billion", "billions", "bn"} or "usd billions" in lowered or "in billions" in lowered:
        return 1_000_000_000.0
    return 1.0


def _is_parenthesized_negative(text: str, start: int, end: int) -> bool:
    """Detect accounting-style negative numbers like ``($1.2)``."""
    before = text[max(0, start - 2) : start]
    after = text[end : min(len(text), end + 2)]
    return "(" in before and ")" in after


def _numbers_match(predicted: float, gold: float, tolerance: float) -> bool:
    """Compare numbers with relative tolerance and a tiny absolute fallback."""
    if gold == 0:
        return abs(predicted) <= tolerance
    return abs(predicted - gold) / abs(gold) <= tolerance


def _extract_boolean_label(text: object, prefer_final: bool = False) -> str | None:
    """Extract a yes/no label from a possibly explanatory answer."""
    normalized = normalize_answer(text)
    if not normalized:
        return None

    answer_match = re.search(r"\banswer\s+(yes|no)\b", normalized)
    if answer_match:
        return answer_match.group(1)

    sentences = re.split(r"[.!?\n]+", str(text or "").strip())
    candidates = list(reversed(sentences)) if prefer_final else sentences
    for sentence in candidates:
        tokens = normalize_answer(sentence).split()
        if not tokens:
            continue
        if tokens[0] in {"yes", "no"}:
            return tokens[0]
        if tokens[-1] in {"yes", "no"}:
            return tokens[-1]

    tokens = normalized.split()
    labels = [token for token in tokens if token in {"yes", "no"}]
    return labels[-1] if prefer_final and labels else (labels[0] if labels else None)


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
