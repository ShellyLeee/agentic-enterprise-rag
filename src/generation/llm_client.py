"""OpenAI-compatible and deterministic mock LLM client."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib import request


@dataclass(frozen=True)
class LLMResponse:
    """Normalized chat completion response."""

    content: str
    model: str
    mode: str


class LLMClient:
    """Minimal chat client with OpenAI-compatible and mock modes."""

    def __init__(
        self,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        mock: bool = False,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.temperature = temperature
        self.mock = mock or not bool(self.api_key)

    def chat(self, *, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a chat completion from the configured backend."""
        if self.mock:
            return LLMResponse(
                content=self._mock_answer(user_prompt),
                model="mock-extractive",
                mode="mock",
            )
        return self._openai_chat(system_prompt=system_prompt, user_prompt=user_prompt)

    def _openai_chat(self, *, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call an OpenAI-compatible `/chat/completions` endpoint."""
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required unless mock mode is enabled.")

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                body: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"OpenAI-compatible chat completion failed: {exc}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected chat completion response: {body}") from exc
        return LLMResponse(content=content, model=self.model, mode="openai-compatible")

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
        """Extract sentence candidates with their context block rank and citation label."""
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

