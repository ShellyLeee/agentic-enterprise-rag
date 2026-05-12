"""Convert RAG-Challenge-2 test-set files into this project's eval JSONL rows."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


QUESTION_TEXT_KEYS = ("text", "question", "question_text", "query", "prompt")
ANSWER_TEXT_KEYS = ("answer", "value", "final_answer", "reference_answer", "ground_truth", "gold_answer")
ID_KEYS = ("id", "question_id", "qid", "uid")
DOC_ID_KEYS = (
    "pdf_sha1",
    "sha1",
    "document_id",
    "doc_id",
    "company_id",
    "company_sha1",
    "source_id",
)
REFERENCE_KEYS = ("references", "reference", "citations", "evidence", "source_documents", "sources")
NA_VALUES = {"", "n/a", "na", "none", "null", "not available"}
COMPARISON_MARKERS = (
    "compare",
    "compared",
    "difference",
    "higher",
    "lower",
    "more than",
    "less than",
    "between",
    "versus",
    " vs ",
)
MULTI_HOP_MARKERS = (
    " and ",
    " both ",
    " combined ",
    " across ",
    " respectively ",
    " together ",
)
METRIC_TERMS = (
    "margin",
    "revenue",
    "profit",
    "income",
    "compensation",
    "buyback",
    "dividend",
    "capex",
    "expenditure",
    "expense",
    "risk",
    "guidance",
    "layoffs",
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "annual",
    "any",
    "are",
    "as",
    "ask",
    "asked",
    "asks",
    "at",
    "available",
    "based",
    "be",
    "by",
    "can",
    "company",
    "context",
    "data",
    "did",
    "do",
    "does",
    "end",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "it",
    "last",
    "mention",
    "mentioned",
    "of",
    "on",
    "or",
    "per",
    "provided",
    "reference",
    "references",
    "report",
    "return",
    "section",
    "sections",
    "such",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "whether",
    "which",
    "with",
    "within",
    "year",
    "according",
    "additionally",
    "although",
    "given",
    "hence",
    "however",
    "i",
    "page",
    "question",
    "since",
    "specifically",
    "therefore",
    "these",
    "throughout",
    "true",
    "false",
    "n",
    "completed",
    "explicitly",
    "first",
    "latest",
    "look",
    "looked",
    "period",
}


@dataclass(frozen=True)
class QuestionRecord:
    """Normalized question entry from questions.json."""

    id: str | None
    text: str
    kind: str | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class AnswerRecord:
    """Normalized answer entry from the reference answer file."""

    id: str | None
    question_text: str | None
    answer: str
    kind: str | None
    references: Any
    reasoning: str
    raw: dict[str, Any]


def load_json(path: str | Path) -> Any:
    """Load a JSON file with a helpful path in parser errors."""
    json_path = Path(path)
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {json_path}: {exc}") from exc


def normalize_lookup(text: object) -> str:
    """Normalize text for question matching."""
    lowered = str(text or "").casefold()
    return re.sub(r"\s+", " ", lowered).strip()


def parse_questions(data: Any) -> list[QuestionRecord]:
    """Parse questions from common list, wrapper, or mapping layouts."""
    entries = _extract_entries(data, wrapper_keys=("questions", "items", "data"), source_name="questions")
    questions: list[QuestionRecord] = []
    for fallback_id, entry in entries:
        if isinstance(entry, str):
            questions.append(QuestionRecord(str(fallback_id) if fallback_id else None, entry.strip(), None, {}))
            continue
        if not isinstance(entry, dict):
            raise ValueError(f"Question entry must be an object or string, got {type(entry).__name__}: {entry!r}")
        text = _first_text(entry, QUESTION_TEXT_KEYS)
        if not text:
            raise ValueError(f"Question entry is missing one of {QUESTION_TEXT_KEYS}: {entry!r}")
        question_id = _first_text(entry, ID_KEYS) or (str(fallback_id) if fallback_id else None)
        questions.append(
            QuestionRecord(
                id=question_id,
                text=text,
                kind=_first_text(entry, ("kind", "type", "answer_type")),
                raw=entry,
            )
        )
    if not questions:
        raise ValueError("No questions found in questions input.")
    return questions


def parse_answers(data: Any) -> list[AnswerRecord]:
    """Parse answers from common list, wrapper, or mapping layouts."""
    entries = _extract_entries(data, wrapper_keys=("answers", "items", "data", "results"), source_name="answers")
    answers: list[AnswerRecord] = []
    for fallback_id, entry in entries:
        if isinstance(entry, (str, bool, int, float)) or entry is None:
            answers.append(
                AnswerRecord(
                    id=str(fallback_id) if fallback_id else None,
                    question_text=None,
                    answer=_stringify_answer(entry),
                    kind=None,
                    references=[],
                    reasoning="",
                    raw={},
                )
            )
            continue
        if not isinstance(entry, dict):
            raise ValueError(f"Answer entry must be an object or scalar, got {type(entry).__name__}: {entry!r}")
        answer_value = _first_present(entry, ANSWER_TEXT_KEYS)
        if answer_value is None:
            raise ValueError(f"Answer entry is missing one of {ANSWER_TEXT_KEYS}: {entry!r}")
        answers.append(
            AnswerRecord(
                id=_first_text(entry, ID_KEYS) or (str(fallback_id) if fallback_id else None),
                question_text=_first_text(entry, ("question_text", "question", "text", "query", "prompt")),
                answer=_stringify_answer(answer_value),
                kind=_first_text(entry, ("kind", "type", "answer_type")),
                references=_first_present(entry, REFERENCE_KEYS) or [],
                reasoning=_first_text(entry, ("reasoning_process", "reasoning", "rationale", "explanation")) or "",
                raw=entry,
            )
        )
    if not answers:
        raise ValueError("No answers found in answer input.")
    return answers


def load_subset(path: str | Path | None) -> list[dict[str, str]]:
    """Load the optional subset CSV."""
    if not path:
        return []
    subset_path = Path(path)
    if not subset_path.exists():
        raise FileNotFoundError(f"Subset CSV not found: {subset_path}")
    with subset_path.open("r", encoding="utf-8", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def convert_records(
    questions: list[QuestionRecord],
    answers: list[AnswerRecord],
    subset_rows: list[dict[str, str]] | None = None,
    max_questions: int | None = None,
) -> list[dict[str, Any]]:
    """Join questions to answers and emit eval-schema dictionaries."""
    subset_rows = subset_rows or []
    answer_by_question = {
        normalize_lookup(answer.question_text): answer for answer in answers if answer.question_text
    }
    answer_by_id = {str(answer.id): answer for answer in answers if answer.id}

    rows: list[dict[str, Any]] = []
    selected_questions = questions[:max_questions] if max_questions is not None else questions
    for index, question in enumerate(selected_questions, start=1):
        answer = _match_answer(question, index, answers, answer_by_question, answer_by_id)
        answer_is_na = is_na_answer(answer.answer)
        row_type = "ood" if answer_is_na else infer_question_type(question.text, subset_rows)
        doc_ids = extract_doc_ids(answer.raw)
        if not doc_ids:
            doc_ids = infer_doc_ids_from_subset(question.text, subset_rows)
        keywords = extract_evidence_keywords(
            answer_text=answer.answer,
            reasoning=answer.reasoning,
            question=question.text,
            include_question_fallback=answer_is_na or normalize_lookup(answer.answer) in {"true", "false"},
        )
        rows.append(
            {
                "id": question.id or answer.id or f"q{index:03d}",
                "question": question.text,
                "answer": answer.answer,
                "type": row_type,
                "gold_doc_ids": doc_ids,
                "gold_evidence_keywords": keywords,
            }
        )
    return rows


def is_na_answer(answer: object) -> bool:
    """Return whether an answer should be treated as unavailable."""
    normalized = normalize_lookup(answer)
    return normalized in NA_VALUES


def infer_question_type(question: str, subset_rows: list[dict[str, str]] | None = None) -> str:
    """Infer this project's eval label using lightweight heuristics."""
    padded = f" {normalize_lookup(question)} "
    if any(marker in padded for marker in COMPARISON_MARKERS):
        return "comparison"

    subset_rows = subset_rows or []
    mentioned_companies = infer_doc_ids_from_subset(question, subset_rows)
    metric_count = sum(1 for term in METRIC_TERMS if term in padded)
    if len(mentioned_companies) > 1 or metric_count > 1:
        return "multi_hop"
    if any(marker in padded for marker in MULTI_HOP_MARKERS) and metric_count > 0:
        return "multi_hop"
    return "simple"


def extract_doc_ids(value: Any) -> list[str]:
    """Extract known document identifiers recursively from an answer object."""
    doc_ids: list[str] = []

    def visit(item: Any, parent_key: str | None = None) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                normalized_key = str(key).casefold()
                if normalized_key in DOC_ID_KEYS and child not in (None, ""):
                    _append_unique(doc_ids, str(child))
                else:
                    visit(child, normalized_key)
        elif isinstance(item, list):
            for child in item:
                visit(child, parent_key)

    visit(value)
    return doc_ids


def infer_doc_ids_from_subset(question: str, subset_rows: list[dict[str, str]]) -> list[str]:
    """Infer PDF SHA1s from company names mentioned in the question."""
    normalized_question = _compact_alnum(question)
    doc_ids: list[str] = []
    for row in subset_rows:
        company_name = row.get("company_name", "")
        sha1 = row.get("sha1", "")
        if not company_name or not sha1:
            continue
        if _compact_alnum(company_name) in normalized_question:
            _append_unique(doc_ids, sha1)
    return doc_ids


def extract_evidence_keywords(
    answer_text: str,
    reasoning: str = "",
    question: str = "",
    include_question_fallback: bool = False,
    max_keywords: int = 8,
) -> list[str]:
    """Extract compact evidence keywords from answer text and sparse-answer context."""
    source = answer_text or ""
    if include_question_fallback or len(_content_tokens(answer_text)) < 2:
        source = " ".join(part for part in (answer_text, reasoning, question) if part)

    keywords: list[str] = []
    for keyword in _numeric_keywords(answer_text, source):
        _append_unique(keywords, keyword)

    for phrase in _capitalized_phrases(source):
        if len(keywords) >= max_keywords:
            break
        _append_unique(keywords, phrase)

    for phrase in _frequent_phrases(source):
        if len(keywords) >= max_keywords:
            break
        _append_unique(keywords, phrase)

    return keywords[:max_keywords]


def write_jsonl(rows: list[dict[str, Any]], path: str | Path) -> None:
    """Write JSONL rows, creating parent directories as needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a compact conversion summary."""
    type_counts = Counter(str(row.get("type", "")) for row in rows)
    return {
        "total": len(rows),
        "count_by_type": dict(sorted(type_counts.items())),
        "na_answers": sum(1 for row in rows if is_na_answer(row.get("answer"))),
    }


def _extract_entries(data: Any, wrapper_keys: tuple[str, ...], source_name: str) -> list[tuple[str | None, Any]]:
    if isinstance(data, list):
        return [(None, item) for item in data]
    if isinstance(data, dict):
        for key in wrapper_keys:
            value = data.get(key)
            if isinstance(value, list):
                return [(None, item) for item in value]
            if isinstance(value, dict):
                return [(str(entry_key), entry_value) for entry_key, entry_value in value.items()]
        if all(isinstance(value, (str, bool, int, float, dict, type(None))) for value in data.values()):
            return [(str(key), value) for key, value in data.items()]
    raise ValueError(
        f"Unsupported {source_name} layout. Expected a list, a wrapper key "
        f"{wrapper_keys}, or an id-to-entry mapping; got {type(data).__name__}."
    )


def _match_answer(
    question: QuestionRecord,
    index: int,
    answers: list[AnswerRecord],
    answer_by_question: dict[str, AnswerRecord],
    answer_by_id: dict[str, AnswerRecord],
) -> AnswerRecord:
    if question.id and question.id in answer_by_id:
        return answer_by_id[question.id]
    matched = answer_by_question.get(normalize_lookup(question.text))
    if matched:
        return matched
    if index <= len(answers):
        return answers[index - 1]
    raise ValueError(f"No reference answer found for question {question.id or index}: {question.text}")


def _first_text(entry: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    value = _first_present(entry, keys)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_present(entry: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in entry:
            return entry[key]
    return None


def _stringify_answer(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _compact_alnum(text: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").casefold())


def _append_unique(items: list[str], value: str) -> None:
    cleaned = re.sub(r"\s+", " ", value).strip(" ,.;:-'\"")
    if cleaned and cleaned not in items:
        items.append(cleaned)


def _content_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_&.-]*|\d+(?:\.\d+)?%?", text)
    cleaned_tokens = [token.strip(" ,.;:-'\"") for token in tokens]
    return [
        token
        for token in cleaned_tokens
        if token
        and token.casefold() not in STOPWORDS
        and not re.fullmatch(r"\d+(?:\.\d+)?%?", token)
    ]


def _capitalized_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    pattern = re.compile(r"\b(?:[A-Z][A-Za-z0-9&'-]*|[A-Z]{2,})(?:\s+(?:[A-Z][A-Za-z0-9&'-]*|[A-Z]{2,}))*")
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        for match in pattern.finditer(sentence):
            phrase = match.group(0).strip()
            if _useful_capitalized_phrase(phrase):
                phrases.append(phrase)
    return phrases


def _frequent_phrases(text: str) -> list[str]:
    tokens = _content_tokens(text)
    lower_tokens = [token.casefold() for token in tokens]
    phrases: list[str] = []
    for size in (3, 2, 1):
        for index in range(0, max(len(lower_tokens) - size + 1, 0)):
            phrase_tokens = lower_tokens[index : index + size]
            if all(token in STOPWORDS for token in phrase_tokens):
                continue
            phrase = " ".join(phrase_tokens)
            if len(phrase) >= 3:
                phrases.append(phrase)
    return phrases


def _numeric_keywords(answer_text: str, source: str) -> list[str]:
    keywords: list[str] = []
    answer_numbers = list(_iter_numbers(answer_text))
    for keyword in answer_numbers:
        _append_unique(keywords, keyword)
    if answer_numbers:
        return keywords

    for keyword in _iter_numbers(source):
        if any(marker in keyword for marker in ("$", "€", "£", "¥", "%", ".", ",")):
            _append_unique(keywords, keyword)
    return keywords


def _iter_numbers(text: str) -> list[str]:
    numbers: list[str] = []
    pattern = re.compile(r"(?:[$€£¥]\s*)?\d[\d,]*(?:\.\d+)?\s*%?")
    for match in pattern.finditer(text):
        end = match.end()
        if end < len(text) and text[end] == "." and "." not in match.group(0):
            continue
        numbers.append(re.sub(r"\s+", "", match.group(0)))
    return numbers


def _useful_capitalized_phrase(phrase: str) -> bool:
    tokens = phrase.split()
    if not tokens:
        return False
    if tokens[0].casefold() in STOPWORDS:
        return False
    if len(tokens) == 1:
        token = tokens[0].strip(" ,.;:-'\"")
        return token.isupper() and len(token) > 1
    return any(token.casefold() not in STOPWORDS for token in tokens)
