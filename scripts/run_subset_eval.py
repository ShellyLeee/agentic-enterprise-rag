#!/usr/bin/env python
"""Run subset-level evaluation by filtering benchmark JSONL then delegating to run_eval.py."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_SUBSETS = {"multi_hop", "ood", "requires_rewrite"}
DEFAULT_SETTINGS = "basic_rag,reranker_rag,iterative_agentic_rag"
SUMMARY_FIELDS = [
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
    parser = argparse.ArgumentParser(description="Run subset evaluation for the custom RAG-Challenge benchmark.")
    parser.add_argument("--dataset", default="rag_challenge_test_set")
    parser.add_argument("--rag_challenge_path", default="data/eval/rag_challenge_test_set.jsonl")
    parser.add_argument("--subset_type", choices=sorted(ALLOWED_SUBSETS), required=True)
    parser.add_argument("--settings", default=DEFAULT_SETTINGS)
    parser.add_argument("--output_dir", default="outputs/subset_eval/")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = _read_jsonl(Path(args.rag_challenge_path))
    subset_rows = [row for row in rows if _matches_subset(row, args.subset_type)]
    if not subset_rows:
        raise SystemExit(f"No examples matched subset_type={args.subset_type!r}")

    subset_dir = Path(args.output_dir) / args.subset_type
    subset_dir.mkdir(parents=True, exist_ok=True)
    settings = [setting.strip() for setting in args.settings.split(",") if setting.strip()]

    with tempfile.TemporaryDirectory(prefix=f"subset_{args.subset_type}_") as tmp_dir:
        subset_path = Path(tmp_dir) / f"tmp_subset_{args.subset_type}.jsonl"
        _write_jsonl(subset_rows, subset_path)
        summary_paths = []
        for setting in settings:
            summary_paths.extend(_run_eval(args.dataset, subset_path, subset_dir, setting))

    summary_rows = [_summary_row(path) for path in summary_paths]
    _write_summary_table(summary_rows, subset_dir / "summary_table.csv")
    _write_markdown_report(
        subset_type=args.subset_type,
        subset_rows=subset_rows,
        summary_rows=summary_rows,
        output_path=subset_dir / "subset_results.md",
    )

    print(f"subset_type={args.subset_type}")
    print(f"num_examples={len(subset_rows)}")
    print(f"output_dir={subset_dir}")
    print(f"summary_table={subset_dir / 'summary_table.csv'}")
    print(f"report={subset_dir / 'subset_results.md'}")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def _matches_subset(row: dict[str, Any], subset_type: str) -> bool:
    if subset_type == "multi_hop":
        return row.get("type") == "multi_hop" or bool(row.get("requires_multi_hop"))
    if subset_type == "ood":
        return row.get("type") == "ood"
    if subset_type == "requires_rewrite":
        return bool(row.get("requires_rewrite"))
    raise ValueError(f"Unsupported subset_type: {subset_type}")


def _run_eval(dataset: str, subset_path: Path, output_dir: Path, setting: str) -> list[Path]:
    before = set(output_dir.glob("*_summary.json"))
    command = [
        sys.executable,
        "scripts/run_eval.py",
        "--dataset",
        dataset,
        "--rag_challenge_path",
        str(subset_path),
        "--setting",
        setting,
        "--output_dir",
        str(output_dir),
    ]
    subprocess.run(command, check=True)
    after = set(output_dir.glob("*_summary.json"))
    created = sorted(after - before)
    if not created:
        raise RuntimeError(f"run_eval.py did not create a summary JSON for setting={setting}")
    return created


def _summary_row(path: Path) -> dict[str, Any]:
    summary = json.loads(path.read_text(encoding="utf-8"))
    overall = summary.get("overall") or summary
    row = {"dataset": summary.get("dataset"), "setting": summary.get("setting")}
    for field in SUMMARY_FIELDS[2:]:
        row[field] = overall.get(field, summary.get(field, 0.0))
    return row


def _write_summary_table(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown_report(
    *,
    subset_type: str,
    subset_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    type_counts = Counter(str(row.get("type") or "unknown") for row in subset_rows)
    source_counts = Counter(str(row.get("source_doc") or "unknown") for row in subset_rows)
    lines = [
        f"# Subset Evaluation: {subset_type}",
        "",
        "## Dataset Statistics",
        "",
        f"- num_examples: {len(subset_rows)}",
        "- category distribution:",
        *_counter_lines(type_counts),
        "- source_doc distribution:",
        *_counter_lines(source_counts),
        "",
        "## Quantitative Results",
        "",
        "| setting | EM | F1 | abstention_rate | rewrite_rate | evidence_gap_rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(summary_rows, key=lambda item: str(item.get("setting"))):
        lines.append(
            "| {setting} | {em:.3f} | {f1:.3f} | {abstain:.3f} | {rewrite:.3f} | {gap:.3f} |".format(
                setting=row.get("setting"),
                em=float(row.get("avg_em") or 0.0),
                f1=float(row.get("avg_f1") or 0.0),
                abstain=float(row.get("abstention_rate") or 0.0),
                rewrite=float(row.get("rewrite_rate") or 0.0),
                gap=float(row.get("evidence_gap_rate") or 0.0),
            )
        )

    lines.extend(["", "## Key Observation", "", _observation(subset_type, summary_rows), ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _counter_lines(counter: Counter[str]) -> list[str]:
    return [f"  - {key}: {value}" for key, value in sorted(counter.items())]


def _observation(subset_type: str, rows: list[dict[str, Any]]) -> str:
    by_setting = {str(row.get("setting")): row for row in rows}
    iterative = by_setting.get("iterative_agentic_rag", {})
    best_baseline_f1 = max(
        [float(row.get("avg_f1") or 0.0) for setting, row in by_setting.items() if setting != "iterative_agentic_rag"],
        default=0.0,
    )
    iterative_f1 = float(iterative.get("avg_f1") or 0.0)
    if subset_type == "multi_hop":
        if iterative_f1 > best_baseline_f1:
            return "- `iterative_agentic_rag` shows stronger multi-hop performance than the single-shot baselines on this subset."
        return "- Multi-hop questions stress cross-chunk retrieval; compare F1 and evidence-gap behavior across settings."
    if subset_type == "requires_rewrite":
        return "- Rewrite-heavy queries are expected to benefit from evidence-gap detection, query rewriting, and retry behavior."
    if subset_type == "ood":
        return "- The OOD subset highlights evidence-aware refusal behavior; abstention and refusal correctness should be inspected alongside F1."
    return "- Inspect subset metrics to compare retrieval difficulty across settings."


if __name__ == "__main__":
    main()
