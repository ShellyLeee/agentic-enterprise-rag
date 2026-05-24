#!/usr/bin/env python
"""Validate a custom RAG-Challenge benchmark JSONL draft."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_TYPES = {"fact_qa", "numerical", "multi_hop", "boolean", "ood"}


def validate_item(item: dict[str, Any], *, line_number: int, seen_ids: set[str]) -> list[str]:
    errors: list[str] = []
    item_id = item.get("id")
    item_type = item.get("type")

    if not item_id:
        errors.append(f"line {line_number}: missing id")
    elif item_id in seen_ids:
        errors.append(f"line {line_number}: duplicate id {item_id}")
    else:
        seen_ids.add(item_id)

    if item_type not in ALLOWED_TYPES:
        errors.append(f"line {line_number}: invalid type {item_type!r}")

    if not item.get("source_doc"):
        errors.append(f"line {line_number}: source_doc is empty")

    answer = item.get("answer")
    evidence = item.get("evidence")
    if item_type != "ood":
        if not answer:
            errors.append(f"line {line_number}: non-OOD answer is empty")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"line {line_number}: non-OOD evidence is empty")

    if evidence is not None and not isinstance(evidence, list):
        errors.append(f"line {line_number}: evidence must be a list")
    elif isinstance(evidence, list):
        for index, evidence_item in enumerate(evidence, start=1):
            if not isinstance(evidence_item, dict):
                errors.append(f"line {line_number}: evidence item {index} must be an object")
                continue
            if not evidence_item.get("evidence_text"):
                errors.append(f"line {line_number}: evidence item {index} has empty evidence_text")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a RAG-Challenge benchmark JSONL file.")
    parser.add_argument("--path", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    seen_ids: set[str] = set()
    type_counts: Counter[str] = Counter()
    total = 0

    with args.path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            total += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            if isinstance(item, dict):
                type_counts[str(item.get("type"))] += 1
                errors.extend(validate_item(item, line_number=line_number, seen_ids=seen_ids))
            else:
                errors.append(f"line {line_number}: row must be a JSON object")

    print("Validation summary")
    print(f"path: {args.path}")
    print(f"rows: {total}")
    print("type_distribution:")
    for item_type in sorted(ALLOWED_TYPES):
        print(f"  {item_type}: {type_counts.get(item_type, 0)}")
    unexpected = {key: value for key, value in type_counts.items() if key not in ALLOWED_TYPES}
    for item_type, count in sorted(unexpected.items()):
        print(f"  {item_type}: {count} (invalid)")

    if errors:
        print("status: FAILED")
        print("errors:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("status: PASSED")


if __name__ == "__main__":
    main()
