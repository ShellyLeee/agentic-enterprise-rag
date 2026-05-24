"""LLM output post-processing helpers."""

from __future__ import annotations

import re


def strip_thinking_blocks(text: str) -> str:
    """Remove Qwen-style thinking traces from generated answers."""
    if not text:
        return text
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"^.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()
