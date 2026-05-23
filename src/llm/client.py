"""OpenAI-compatible LLM client.

The project talks to local and remote chat models through the OpenAI chat
completion protocol. For local experiments, the default target is a vLLM
OpenAI-compatible server serving Qwen3-8B.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMResponse:
    """Normalized chat completion response."""

    content: str
    model: str
    mode: str


class LLMClient:
    """Small OpenAI-compatible chat client with an explicit mock mode.

    Parameters can be supplied as a flat dict, a config dict containing an
    ``llm`` section, or legacy keyword arguments used by the existing scripts.
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        mock: bool | None = None,
    ) -> None:
        raw_config = config or {}
        llm_config = raw_config.get("llm", raw_config) if isinstance(raw_config, dict) else {}

        self.provider = str(llm_config.get("provider", "openai_compatible"))
        self.base_url = str(
            base_url
            or llm_config.get("base_url")
            or os.getenv("OPENAI_BASE_URL")
            or "http://localhost:8000/v1"
        ).rstrip("/")
        self.api_key = str(api_key or llm_config.get("api_key") or os.getenv("OPENAI_API_KEY") or "EMPTY")
        self.model_name = str(
            model_name
            or model
            or llm_config.get("model_name")
            or llm_config.get("model")
            or os.getenv("OPENAI_MODEL")
            or "qwen3-8b"
        )
        self.temperature = float(
            temperature if temperature is not None else llm_config.get("temperature", 0.0)
        )
        configured_max_tokens = max_tokens if max_tokens is not None else llm_config.get("max_tokens", 512)
        self.max_tokens = int(configured_max_tokens) if configured_max_tokens is not None else None
        self.timeout = float(timeout if timeout is not None else llm_config.get("timeout", 120))
        self.mock = bool(mock if mock is not None else llm_config.get("mock", False))

    def generate(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate text from chat messages and return assistant content."""
        if not messages:
            raise ValueError("messages cannot be empty.")
        if self.mock:
            return self._mock_answer(str(messages[-1].get("content", "")))

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is required for real LLM calls. "
                "Install dependencies with `pip install -r requirements.txt`."
            ) from exc

        request_kwargs: dict[str, Any] = {
            "model": kwargs.pop("model_name", kwargs.pop("model", self.model_name)),
            "messages": messages,
            "temperature": kwargs.pop("temperature", self.temperature),
        }
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens
        request_kwargs.update(kwargs)

        try:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
            response = client.chat.completions.create(**request_kwargs)
        except Exception as exc:
            raise RuntimeError(
                "Failed to call the OpenAI-compatible LLM API at "
                f"{self.base_url}. If you are using the local Qwen3-8B setup, "
                "start the vLLM server first with `bash scripts/serve_qwen3_8b_vllm.sh`. "
                f"Original error: {exc}"
            ) from exc

        content = response.choices[0].message.content
        return (content or "").strip()

    def generate_from_prompt(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from a user prompt plus an optional system prompt."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self.generate(messages, **kwargs)

    def chat(self, *, system_prompt: str, user_prompt: str, **kwargs: Any) -> LLMResponse:
        """Backward-compatible chat wrapper used by existing RAG components."""
        content = self.generate_from_prompt(user_prompt, system_prompt=system_prompt, **kwargs)
        return LLMResponse(
            content=content,
            model="mock-extractive" if self.mock else self.model_name,
            mode="mock" if self.mock else "openai-compatible",
        )

    def _mock_answer(self, user_prompt: str) -> str:
        """Produce a deterministic extractive answer from the provided context."""
        question = self._extract_between(user_prompt, "Question:", "Context:").strip()
        context = self._extract_between(user_prompt, "Context:", "Answer:").strip()
        if not context:
            return "I don't know based on the provided context."

        question_terms = self._terms(question)
        candidates = self._context_sentences(context)
        if not candidates:
            return "I don't know based on the provided context."

        ranked = sorted(
            candidates,
            key=lambda item: (self._score_sentence(item[0], question_terms), -item[1]),
            reverse=True,
        )
        best_sentence, _, citation = ranked[0]
        if self._score_sentence(best_sentence, question_terms) == 0:
            return "I don't know based on the provided context."
        return f"{best_sentence} {citation}".strip()

    @staticmethod
    def _extract_between(text: str, start: str, end: str) -> str:
        """Extract text between two labels."""
        start_index = text.find(start)
        if start_index == -1:
            return ""
        start_index += len(start)
        end_index = text.find(end, start_index)
        return text[start_index:] if end_index == -1 else text[start_index:end_index]

    @staticmethod
    def _terms(text: str) -> set[str]:
        """Tokenize important terms for deterministic mock scoring."""
        stopwords = {
            "a",
            "an",
            "and",
            "are",
            "do",
            "does",
            "how",
            "is",
            "many",
            "of",
            "the",
            "to",
            "what",
            "when",
            "where",
            "who",
        }
        return {
            token
            for token in re.findall(r"[a-z0-9]+", text.lower())
            if len(token) > 2 and token not in stopwords
        }

    @staticmethod
    def _context_sentences(context: str) -> list[tuple[str, int, str]]:
        """Extract sentence candidates with their context block rank and label."""
        candidates: list[tuple[str, int, str]] = []
        blocks = re.split(r"\n\s*\[chunk:", context)
        for block_index, block in enumerate(blocks):
            if not block.strip():
                continue
            block_text = block if block_index == 0 else "[chunk:" + block
            citation_match = re.search(r"(\[chunk:[^\]]+\])", block_text)
            citation = citation_match.group(1) if citation_match else ""
            clean = re.sub(r"\[chunk:[^\]]+\]\s*", "", block_text)
            clean = re.sub(r"\s+", " ", clean).strip()
            for sentence in re.split(r"(?<=[.!?])\s+", clean):
                sentence = sentence.strip()
                if sentence:
                    candidates.append((sentence, block_index, citation))
        return candidates

    @staticmethod
    def _score_sentence(sentence: str, question_terms: set[str]) -> int:
        """Score sentence overlap with question terms."""
        sentence_terms = LLMClient._terms(sentence)
        return len(sentence_terms & question_terms)
