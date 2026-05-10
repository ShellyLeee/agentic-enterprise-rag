"""Evaluation dataset loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal["simple", "comparison", "multi_hop", "ood"]


class EvalQuestion(BaseModel):
    """One JSONL evaluation row."""

    id: str
    question: str
    answer: str
    type: QuestionType
    gold_doc_ids: list[str] = Field(default_factory=list)
    gold_evidence_keywords: list[str] = Field(default_factory=list)


def load_eval_dataset(path: str | Path) -> list[EvalQuestion]:
    """Load and validate an evaluation JSONL file."""
    eval_path = Path(path)
    if not eval_path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {eval_path}")

    rows: list[EvalQuestion] = []
    with eval_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(EvalQuestion.model_validate_json(stripped))
            except Exception as exc:
                raise ValueError(f"Invalid eval row at {eval_path}:{line_number}: {exc}") from exc

    if not rows:
        raise ValueError(f"Evaluation file contains no rows: {eval_path}")
    ids = [row.id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Evaluation file contains duplicate IDs: {eval_path}")
    return rows

