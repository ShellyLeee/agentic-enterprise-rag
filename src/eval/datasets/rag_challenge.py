"""Custom RAG-Challenge PDF benchmark loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.schema import QAExample


def load_rag_challenge_test_set(
    path: str | Path = "data/eval/rag_challenge_test_set.jsonl",
    max_examples: int | None = None,
) -> list[QAExample]:
    """Load the custom RAG-Challenge benchmark JSONL."""
    benchmark_path = Path(path)
    if not benchmark_path.exists():
        raise FileNotFoundError(f"RAG-Challenge benchmark file not found: {benchmark_path}")

    examples: list[QAExample] = []
    with benchmark_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            examples.append(_row_to_example(row, benchmark_path, line_number))
            if max_examples is not None and len(examples) >= max_examples:
                break
    return examples


def _row_to_example(row: dict[str, Any], path: Path, line_number: int) -> QAExample:
    """Convert one benchmark row into the shared QAExample schema."""
    evidence = row.get("evidence") or []
    if not isinstance(evidence, list):
        raise ValueError(f"Invalid evidence list on line {line_number} of {path}")

    gold_evidence = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        gold_evidence.append(
            {
                "chunk_id": item.get("chunk_id"),
                "doc_name": item.get("doc_name"),
                "source_doc": item.get("doc_name") or row.get("source_doc"),
                "page_num": item.get("page_num"),
                "text": item.get("evidence_text") or "",
                "evidence_text": item.get("evidence_text") or "",
            }
        )

    answer = str(row.get("answer") or "")
    return QAExample(
        id=str(row.get("id") or f"{path.stem}-{line_number}"),
        question=str(row.get("question") or ""),
        answers=[answer] if answer else [],
        documents=None,
        gold_evidence=gold_evidence,
        metadata={
            "dataset": "rag_challenge_test_set",
            "source_file": str(path),
            "type": row.get("type"),
            "source_doc": row.get("source_doc"),
            "difficulty": row.get("difficulty"),
            "requires_rewrite": bool(row.get("requires_rewrite", False)),
            "requires_multi_hop": bool(row.get("requires_multi_hop", False)),
            "notes": row.get("notes"),
            "evidence": evidence,
        },
    )
