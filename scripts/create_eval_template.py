"""Create an example evaluation JSONL template."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_SOURCE = Path("data/eval/eval_questions.example.jsonl")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Create an evaluation JSONL template.")
    parser.add_argument("--output", default="data/eval/eval_questions.template.jsonl")
    return parser


def main() -> None:
    """Copy the example eval set to a user-editable template."""
    args = build_parser().parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DEFAULT_SOURCE, output)
    print(f"Wrote evaluation template to {output}")


if __name__ == "__main__":
    main()

