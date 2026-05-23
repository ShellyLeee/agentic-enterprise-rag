"""Benchmark dataset loaders."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.eval.schema import QAExample


def load_hotpotqa(max_examples: int | None = None, split: str = "validation") -> list[QAExample]:
    """Load HotpotQA distractor examples through HuggingFace Datasets."""
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "HotpotQA loading requires HuggingFace datasets. "
            "Install dependencies with `pip install -r requirements.txt`."
        ) from exc

    try:
        dataset = load_dataset("hotpot_qa", "distractor", split=split)
    except Exception as exc:
        raise RuntimeError(f"Failed to load HotpotQA split '{split}' from HuggingFace datasets: {exc}") from exc

    if max_examples is not None:
        dataset = dataset.select(range(min(max_examples, len(dataset))))

    examples: list[QAExample] = []
    for row in dataset:
        context = row.get("context") or {}
        titles = list(context.get("title") or [])
        sentences = list(context.get("sentences") or [])
        documents = [
            {
                "title": str(title),
                "text": " ".join(str(sentence) for sentence in sentence_group),
                "source": "hotpotqa",
            }
            for title, sentence_group in zip(titles, sentences)
        ]

        supporting = row.get("supporting_facts") or {}
        sf_titles = list(supporting.get("title") or [])
        sf_sentence_ids = list(supporting.get("sent_id") or [])
        gold_evidence = []
        docs_by_title = {doc["title"]: doc for doc in documents}
        for title, sent_id in zip(sf_titles, sf_sentence_ids):
            doc = docs_by_title.get(str(title), {})
            gold_evidence.append(
                {
                    "title": str(title),
                    "sent_id": sent_id,
                    "text": _sentence_at(doc.get("text", ""), sent_id),
                    "source": "hotpotqa",
                }
            )

        examples.append(
            QAExample(
                id=str(row.get("id") or row.get("_id") or len(examples)),
                question=str(row.get("question", "")),
                answers=[str(row.get("answer", ""))],
                documents=documents,
                gold_evidence=gold_evidence,
                metadata={
                    "dataset": "hotpotqa",
                    "split": split,
                    "type": row.get("type"),
                    "level": row.get("level"),
                },
            )
        )
    return examples


def load_financebench_sample(
    data_dir: str | Path = "data/financebench",
    max_examples: int | None = None,
) -> list[QAExample]:
    """Load local FinanceBench sample files from JSON, JSONL, or CSV.

    The parser accepts common field names for question, answer, and context so
    small public samples or hand-curated subsets can be evaluated consistently.
    """
    root = Path(data_dir)
    if not root.exists():
        raise FileNotFoundError(
            "FinanceBench sample data was not found at data/financebench/. "
            "Create that directory and place a JSON, JSONL, or CSV sample file there."
        )

    files = sorted(
        [
            path
            for path in root.iterdir()
            if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".csv"}
        ]
    )
    if not files:
        raise FileNotFoundError(f"No JSON, JSONL, or CSV files found in {root}.")

    examples: list[QAExample] = []
    for path in files:
        for raw_row in _read_rows(path):
            example = _financebench_row_to_example(raw_row, path, len(examples))
            if example is not None:
                examples.append(example)
                if max_examples is not None and len(examples) >= max_examples:
                    return examples
    return examples


def load_financebench(
    max_examples: int | None = None,
    source: str = "hf",
    local_path: str | None = None,
) -> list[QAExample]:
    """Load FinanceBench from HuggingFace or local sample files.

    ``source="hf"`` loads the 150-example open-source sample from
    ``PatronusAI/financebench``. ``source="local"`` preserves the existing
    JSON/JSONL/CSV sample loader. ``source="auto"`` tries HuggingFace first and
    falls back to local files when HuggingFace is unavailable.
    """
    normalized_source = source.lower().strip()
    if normalized_source == "hf":
        return _load_financebench_hf(max_examples=max_examples)
    if normalized_source == "local":
        return _load_financebench_local(local_path=local_path, max_examples=max_examples)
    if normalized_source == "auto":
        try:
            return _load_financebench_hf(max_examples=max_examples)
        except RuntimeError as hf_exc:
            try:
                return _load_financebench_local(local_path=local_path, max_examples=max_examples)
            except Exception as local_exc:
                raise RuntimeError(
                    "Failed to load FinanceBench from HuggingFace and local fallback. "
                    f"HuggingFace error: {hf_exc}. Local error: {local_exc}"
                ) from local_exc
    raise ValueError("source must be one of: hf, local, auto.")


def _load_financebench_hf(max_examples: int | None = None) -> list[QAExample]:
    """Load the HuggingFace FinanceBench train split."""
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError(
            "FinanceBench HuggingFace loading requires the datasets package. "
            "Install dependencies with `pip install -r requirements.txt`, or use "
            "`--financebench_source local` with a local JSON/JSONL/CSV sample."
        ) from exc

    try:
        dataset = load_dataset("PatronusAI/financebench", split="train")
    except Exception as exc:
        raise RuntimeError(
            "Failed to load PatronusAI/financebench from HuggingFace. "
            "Check network access/HuggingFace availability, or use "
            "`--financebench_source local --financebench_local_path ...`."
        ) from exc

    if max_examples is not None:
        dataset = dataset.select(range(min(max_examples, len(dataset))))
    return [_financebench_hf_row_to_example(dict(row), index) for index, row in enumerate(dataset)]


def _load_financebench_local(
    local_path: str | None,
    max_examples: int | None = None,
) -> list[QAExample]:
    """Load local FinanceBench samples from a file or directory."""
    path = Path(local_path or "data/financebench")
    if path.is_file():
        examples = []
        for index, raw_row in enumerate(_read_rows(path)):
            example = _financebench_row_to_example(raw_row, path, index)
            if example is not None:
                examples.append(example)
                if max_examples is not None and len(examples) >= max_examples:
                    return examples
        return examples
    return load_financebench_sample(path, max_examples=max_examples)


def _financebench_hf_row_to_example(raw_row: dict[str, Any], index: int) -> QAExample:
    """Convert one PatronusAI/financebench row to ``QAExample``."""
    financebench_id = str(raw_row.get("financebench_id") or f"financebench-{index}")
    evidence_items = _evidence_items(raw_row.get("evidence"))

    documents = []
    gold_evidence = []
    for evidence_index, evidence in enumerate(evidence_items):
        doc_name = evidence.get("doc_name") or raw_row.get("doc_name")
        text = evidence.get("evidence_text_full_page") or evidence.get("evidence_text") or ""
        documents.append(
            {
                "id": f"{financebench_id}_evidence_{evidence_index}",
                "title": doc_name,
                "text": text,
                "source": "financebench_evidence",
                "page_num": evidence.get("evidence_page_num"),
                "doc_name": doc_name,
            }
        )
        gold_evidence.append(
            {
                "title": doc_name,
                "doc_name": doc_name,
                "text": evidence.get("evidence_text") or "",
                "full_page_text": evidence.get("evidence_text_full_page") or "",
                "page_num": evidence.get("evidence_page_num"),
            }
        )

    answer = raw_row.get("answer")
    return QAExample(
        id=financebench_id,
        question=str(raw_row.get("question") or ""),
        answers=[str(answer)] if answer else [],
        documents=documents,
        gold_evidence=gold_evidence,
        metadata={
            "company": raw_row.get("company"),
            "doc_name": raw_row.get("doc_name"),
            "question_type": raw_row.get("question_type"),
            "question_reasoning": raw_row.get("question_reasoning"),
            "domain_question_num": raw_row.get("domain_question_num"),
            "justification": raw_row.get("justification"),
            "dataset_subset_label": raw_row.get("dataset_subset_label"),
            "gics_sector": raw_row.get("gics_sector"),
            "doc_type": raw_row.get("doc_type"),
            "doc_period": raw_row.get("doc_period"),
            "doc_link": raw_row.get("doc_link"),
            "dataset": "financebench",
            "source": "hf",
        },
    )


def _read_rows(path: Path) -> list[dict[str, Any]]:
    """Read row dictionaries from a JSON, JSONL, or CSV file."""
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if stripped:
                    rows.append(json.loads(stripped))
        return rows
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("examples", "data", "rows", "questions"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        return [data]
    return []


def _evidence_items(evidence: Any) -> list[dict[str, Any]]:
    """Normalize FinanceBench evidence into a list of dictionaries."""
    if evidence is None:
        return []
    if isinstance(evidence, str):
        try:
            decoded = json.loads(evidence)
        except json.JSONDecodeError:
            return [{"evidence_text": evidence}]
        return _evidence_items(decoded)
    if isinstance(evidence, dict):
        if any(isinstance(value, list) for value in evidence.values()):
            max_len = max((len(value) for value in evidence.values() if isinstance(value, list)), default=0)
            items = []
            for index in range(max_len):
                item = {}
                for key, value in evidence.items():
                    item[key] = value[index] if isinstance(value, list) and index < len(value) else value
                items.append(item)
            return items
        return [evidence]
    if isinstance(evidence, list):
        items = []
        for item in evidence:
            if isinstance(item, dict):
                items.append(item)
            elif isinstance(item, str):
                items.append({"evidence_text": item})
        return items
    return []


def _financebench_row_to_example(raw_row: dict[str, Any], path: Path, index: int) -> QAExample | None:
    """Convert one loose FinanceBench-style row to ``QAExample``."""
    question = _first_text(raw_row, ["question", "query", "prompt"])
    answer = _first_text(raw_row, ["answer", "gold_answer", "reference_answer", "expected_answer"])
    if not question or not answer:
        return None

    documents = _documents_from_row(raw_row)
    gold_evidence = _gold_evidence_from_row(raw_row, documents)
    return QAExample(
        id=str(
            raw_row.get("financebench_id")
            or raw_row.get("id")
            or raw_row.get("example_id")
            or raw_row.get("question_id")
            or f"{path.stem}-{index}"
        ),
        question=question,
        answers=[answer],
        documents=documents,
        gold_evidence=gold_evidence,
        metadata={
            "dataset": "financebench",
            "source_file": str(path),
            **{key: value for key, value in raw_row.items() if key not in {"documents", "context", "contexts"}},
        },
    )


def _documents_from_row(raw_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract candidate context documents from flexible row formats."""
    candidates = (
        raw_row.get("documents")
        or raw_row.get("context")
        or raw_row.get("contexts")
        or raw_row.get("evidence")
        or raw_row.get("references")
    )
    if isinstance(candidates, str):
        return [{"title": str(raw_row.get("title") or raw_row.get("company") or "context"), "text": candidates, "source": "financebench"}]
    if isinstance(candidates, dict):
        candidates = [candidates]
    if not isinstance(candidates, list):
        return []

    documents = []
    for item in candidates:
        if isinstance(item, str):
            documents.append({"title": "context", "text": item, "source": "financebench"})
            continue
        if not isinstance(item, dict):
            continue
        text = _first_text(
            item,
            ["evidence_text_full_page", "evidence_text", "text", "content", "context", "paragraph", "excerpt"],
        )
        if not text:
            continue
        documents.append(
            {
                "id": str(item.get("id") or item.get("evidence_id") or f"evidence-{len(documents)}"),
                "title": str(item.get("title") or item.get("doc_name") or item.get("company") or "context"),
                "text": text,
                "source": str(item.get("source") or item.get("filename") or item.get("doc_name") or "financebench"),
                "page_num": item.get("evidence_page_num") or item.get("page_num"),
                "doc_name": item.get("doc_name"),
                "metadata": {key: value for key, value in item.items() if key not in {"text", "content", "context"}},
            }
        )
    return documents


def _gold_evidence_from_row(
    raw_row: dict[str, Any],
    documents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract gold evidence hints or fall back to all local documents."""
    evidence = raw_row.get("gold_evidence") or raw_row.get("supporting_evidence") or raw_row.get("evidence")
    if isinstance(evidence, dict):
        evidence = [evidence]
    if isinstance(evidence, list):
        parsed = []
        for item in evidence:
            if isinstance(item, str):
                parsed.append({"text": item, "source": "financebench"})
            elif isinstance(item, dict):
                parsed.append(
                    {
                        "title": str(item.get("title") or item.get("doc_name") or item.get("source") or ""),
                        "doc_name": item.get("doc_name"),
                        "text": _first_text(item, ["evidence_text", "text", "content", "excerpt", "sentence"]),
                        "full_page_text": item.get("evidence_text_full_page") or "",
                        "page_num": item.get("evidence_page_num") or item.get("page_num"),
                        "source": str(item.get("source") or item.get("filename") or "financebench"),
                    }
                )
        if parsed:
            return parsed
    return [{"title": doc.get("title", ""), "text": doc.get("text", ""), "source": doc.get("source", "")} for doc in documents]


def _first_text(row: dict[str, Any], keys: list[str]) -> str:
    """Return the first non-empty string value from a row."""
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _sentence_at(text: str, sent_id: Any) -> str:
    """Best-effort sentence lookup from concatenated document text."""
    try:
        index = int(sent_id)
    except (TypeError, ValueError):
        return ""
    sentences = [sentence.strip() for sentence in text.split(". ") if sentence.strip()]
    if 0 <= index < len(sentences):
        return sentences[index]
    return ""
