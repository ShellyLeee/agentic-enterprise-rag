"""Question category tagging for benchmark analysis."""

from __future__ import annotations

import re

from src.eval.schema import QAExample


def categorize_example(example: QAExample, dataset_name: str) -> list[str]:
    """Return dataset-aware categories for a QA example."""
    dataset = dataset_name.lower()
    if dataset == "financebench":
        return _financebench_categories(example)
    if dataset == "hotpotqa":
        return _hotpotqa_categories(example)
    return ["unknown"]


def _financebench_categories(example: QAExample) -> list[str]:
    """Tag FinanceBench examples by reasoning/question style."""
    metadata = example.metadata or {}
    question = example.question.lower()
    question_type = str(metadata.get("question_type") or "").lower()
    reasoning = str(metadata.get("question_reasoning") or "").lower()
    categories = ["finance", "domain_specific"]

    if "metric" in question_type or "numerical" in reasoning or "number" in reasoning:
        categories.append("numerical")
    if "information extraction" in reasoning:
        categories.append("fact_qa")
        if re.search(r"\bnumber|amount|value|percent|percentage|ratio|revenue|income|cash|debt|assets?\b", question):
            categories.append("numerical")
    if _is_boolean_question(example):
        categories.append("boolean")
    if "logical reasoning" in reasoning:
        categories.append("logical_reasoning")
    if any(term in question for term in ("balance sheet", "cash flow statement", "income statement")):
        categories.append("table_or_statement_qa")

    return _unique(categories)


def _hotpotqa_categories(example: QAExample) -> list[str]:
    """Tag HotpotQA examples by task type and difficulty."""
    metadata = example.metadata or {}
    categories = ["multi_hop"]
    question_type = str(metadata.get("type") or "").lower()
    level = str(metadata.get("level") or "").lower()
    if question_type in {"bridge", "comparison"}:
        categories.append(question_type)
    if level in {"hard", "medium", "easy"}:
        categories.append(level)
    categories.append("boolean" if _gold_is_boolean(example) else "fact_qa")
    return _unique(categories)


def _is_boolean_question(example: QAExample) -> bool:
    """Return true for yes/no style questions or answers."""
    if _gold_is_boolean(example):
        return True
    return bool(re.match(r"\s*(is|are|was|were|does|did|can|should)\b", example.question.lower()))


def _gold_is_boolean(example: QAExample) -> bool:
    """Return true if any gold answer starts with yes/no."""
    return any(str(answer).strip().lower().startswith(("yes", "no")) for answer in example.answers)


def _unique(values: list[str]) -> list[str]:
    """Preserve category order while removing duplicates."""
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
