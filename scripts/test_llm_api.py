"""Smoke test the configured OpenAI-compatible LLM API."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.llm import LLMClient


TEST_SYSTEM_PROMPT = (
    "You are a concise and reliable question-answering assistant. "
    "Do not output chain-of-thought, hidden reasoning, or <think> blocks. "
    "Only provide the final answer. "
    "When context is provided, answer based on the context. If the context is insufficient, say you are not sure."
)


def load_config(path: Path) -> dict[str, Any]:
    """Load YAML config."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(description="Test the local OpenAI-compatible LLM API.")
    parser.add_argument("--config", default="configs/llm.yaml", help="YAML config path.")
    parser.add_argument(
        "--question",
        default="Who wrote the novel Pride and Prejudice?",
        help="Question to send to the model.",
    )
    return parser


def main() -> None:
    """Call the configured LLM and print its answer."""
    args = build_parser().parse_args()
    config = load_config(Path(args.config))
    client = LLMClient(config)
    try:
        generation = client.generate_from_prompt_with_raw(args.question, system_prompt=TEST_SYSTEM_PROMPT)
    except RuntimeError as exc:
        raise SystemExit(
            f"LLM API test failed: {exc}\n"
            "Make sure the vLLM server is running, for example: "
            "`bash scripts/serve_qwen3_8b_vllm.sh`."
        ) from exc

    print("Question")
    print(args.question)
    print("\nRaw Answer")
    print(generation.raw_prediction)
    print("\nCleaned Answer")
    print(generation.prediction)
    if "<think" in generation.prediction.lower() or "</think>" in generation.prediction.lower():
        raise SystemExit("Cleaned answer still contains a <think> tag.")


if __name__ == "__main__":
    main()
