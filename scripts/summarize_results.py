"""Summarize benchmark summary JSON files into one comparison table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


FIELDS = [
    "dataset",
    "setting",
    "num_examples",
    "avg_em",
    "avg_f1",
    "numeric_match",
    "boolean_acc",
    "retrieval_hit_rate",
    "evidence_recall_at_k",
    "mrr",
    "abstention_rate",
    "avg_retry_count",
    "rewrite_rate",
    "evidence_gap_rate",
    "avg_latency_sec",
]


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Summarize benchmark result summaries.")
    parser.add_argument("--input_dir", default="outputs/eval_results", help="Directory containing *_summary.json files.")
    parser.add_argument("--output", help="CSV output path. Defaults to <input_dir>/summary_table.csv.")
    return parser


def main() -> None:
    """Read summary JSON files and write/print a comparison table."""
    args = build_parser().parse_args()
    input_dir = Path(args.input_dir)
    output_path = Path(args.output) if args.output else input_dir / "summary_table.csv"
    rows = [_row_from_summary(path) for path in sorted(input_dir.glob("*_summary.json"))]
    if not rows:
        raise SystemExit(f"No *_summary.json files found in {input_dir}.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(_markdown_table(rows))
    print(f"\nWrote CSV summary to {output_path}")


def _row_from_summary(path: Path) -> dict[str, Any]:
    """Convert one summary JSON into a flat table row."""
    summary = json.loads(path.read_text(encoding="utf-8"))
    overall = summary.get("overall") or summary
    row = {"dataset": summary.get("dataset"), "setting": summary.get("setting")}
    for field in FIELDS[2:]:
        row[field] = overall.get(field, summary.get(field, 0.0))
    return row


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    """Render rows as a compact markdown table."""
    lines = [
        "| " + " | ".join(FIELDS) + " |",
        "| " + " | ".join(["---"] * len(FIELDS)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_cell(row.get(field)) for field in FIELDS) + " |")
    return "\n".join(lines)


def _format_cell(value: Any) -> str:
    """Format one table cell."""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


if __name__ == "__main__":
    main()
