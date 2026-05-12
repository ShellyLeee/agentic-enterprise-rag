"""Convert a local RAG-Challenge-2 test_set into eval JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.rag_challenge_converter import (
    convert_records,
    load_json,
    load_subset,
    parse_answers,
    parse_questions,
    summarize_rows,
    write_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Convert RAG-Challenge-2 test_set files to eval JSONL.")
    parser.add_argument("--questions", required=True, help="Path to questions.json.")
    parser.add_argument("--answers", required=True, help="Path to reference answers JSON.")
    parser.add_argument("--subset", help="Optional subset.csv with company and SHA1 metadata.")
    parser.add_argument("--output", required=True, help="Output eval JSONL path.")
    parser.add_argument("--max_questions", type=int, help="Optional limit for debugging.")
    return parser


def main() -> None:
    """Run conversion and print a summary."""
    args = build_parser().parse_args()
    questions = parse_questions(load_json(args.questions))
    answers = parse_answers(load_json(args.answers))
    subset_rows = load_subset(args.subset)
    rows = convert_records(
        questions=questions,
        answers=answers,
        subset_rows=subset_rows,
        max_questions=args.max_questions,
    )
    write_jsonl(rows, args.output)

    summary = summarize_rows(rows)
    print(f"total examples: {summary['total']}")
    print(f"count by type: {summary['count_by_type']}")
    print(f"count with N/A answers: {summary['na_answers']}")
    print(f"output path: {args.output}")


if __name__ == "__main__":
    main()
