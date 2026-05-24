"""Backward-compatible import path for the unified LLM client."""

from src.llm.client import LLMClient, LLMGeneration, LLMResponse

__all__ = ["LLMClient", "LLMGeneration", "LLMResponse"]
