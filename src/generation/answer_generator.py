"""Naive RAG answer generation from retrieved chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.generation.llm_client import LLMClient
from src.prompts.rag_prompts import GROUNDED_QA_SYSTEM_PROMPT, GROUNDED_QA_USER_PROMPT


@dataclass(frozen=True)
class GeneratedAnswer:
    """Naive RAG answer payload."""

    question: str
    answer: str
    citations: list[dict[str, Any]]
    retrieved_chunks: list[dict[str, Any]]
    llm_mode: str
    llm_model: str


class AnswerGenerator:
    """Formats retrieval context and generates grounded answers."""

    def __init__(self, llm_client: LLMClient, *, max_context_chunks: int = 5) -> None:
        self.llm_client = llm_client
        self.max_context_chunks = max_context_chunks

    def generate(self, question: str, retrieved_chunks: list[dict[str, Any]]) -> GeneratedAnswer:
        """Generate an answer using the retrieved chunks as the only context."""
        context_chunks = retrieved_chunks[: self.max_context_chunks]
        metadata_answer = self._metadata_company_answer(question, context_chunks)
        if metadata_answer and self.llm_client.mock:
            return GeneratedAnswer(
                question=question,
                answer=metadata_answer,
                citations=self._citations_from_chunks(context_chunks),
                retrieved_chunks=context_chunks,
                llm_mode="mock",
                llm_model="metadata-aware-mock",
            )

        context = self._format_context(context_chunks)
        user_prompt = GROUNDED_QA_USER_PROMPT.format(question=question, context=context)
        response = self.llm_client.chat(
            system_prompt=GROUNDED_QA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return GeneratedAnswer(
            question=question,
            answer=response.content.strip(),
            citations=self._citations_from_chunks(context_chunks),
            retrieved_chunks=context_chunks,
            llm_mode=response.mode,
            llm_model=response.model,
        )

    def _format_context(self, chunks: list[dict[str, Any]]) -> str:
        """Render chunks with source labels for grounded prompting."""
        parts = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            label = self._citation_label(index, chunk)
            if metadata.get("type") == "metadata_lookup":
                source = metadata.get("source_id") or metadata.get("file_name") or "unknown source"
                company_name = metadata.get("company_name") or "unknown company"
                parts.append(
                    f"{label}\n"
                    f"[Document Metadata] source={source} company_name={company_name}\n"
                    f"text: {chunk.get('text', '')}"
                )
                continue
            source = metadata.get("file_name") or metadata.get("source_path") or "unknown source"
            page = metadata.get("page_number")
            section = metadata.get("section_title") or "unknown section"
            parts.append(
                f"{label}\n"
                f"source: {source}\n"
                f"page: {page}\n"
                f"section: {section}\n"
                f"score: {chunk.get('score')}\n"
                f"text: {chunk.get('text', '')}"
            )
        return "\n\n---\n\n".join(parts)

    def _citations_from_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Build citation records from retrieval metadata."""
        citations = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            citations.append(
                {
                    "label": self._citation_label(index, chunk),
                    "chunk_id": chunk.get("chunk_id"),
                    "source_path": metadata.get("source_path"),
                    "file_name": metadata.get("file_name"),
                    "page_number": metadata.get("page_number"),
                    "section_title": metadata.get("section_title"),
                    "type": metadata.get("type"),
                    "score": chunk.get("score"),
                }
            )
        return citations

    def _metadata_company_answer(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        """Synthesize company identity answers when metadata completes report evidence."""
        if not re.search(r"\b(which|what)\s+compan(?:y|ies)\b", question.lower()):
            return None

        supporting_index, supporting_chunk = self._top_text_chunk(chunks)
        if supporting_chunk is None:
            return None

        metadata_match = self._matching_metadata_chunk(supporting_chunk, chunks)
        if not metadata_match:
            return None
        metadata_index, metadata_chunk = metadata_match
        company_name = str(metadata_chunk.get("metadata", {}).get("company_name") or "").strip()
        if not company_name:
            return None

        sentence = self._supporting_sentence(question, supporting_chunk)
        if not sentence:
            return None
        sentence = self._replace_generic_company(sentence, company_name)
        if company_name.lower() not in sentence.lower():
            sentence = f"{company_name} {sentence[0].lower() + sentence[1:]}"

        metadata_label = self._citation_label(metadata_index, metadata_chunk)
        chunk_label = self._citation_label(supporting_index, supporting_chunk)
        return f"{sentence} {metadata_label} {chunk_label}".strip()

    @staticmethod
    def _top_text_chunk(chunks: list[dict[str, Any]]) -> tuple[int, dict[str, Any] | None]:
        for index, chunk in enumerate(chunks, start=1):
            if chunk.get("metadata", {}).get("type") != "metadata_lookup":
                return index, chunk
        return 0, None

    def _matching_metadata_chunk(
        self,
        supporting_chunk: dict[str, Any],
        chunks: list[dict[str, Any]],
    ) -> tuple[int, dict[str, Any]] | None:
        supporting_sources = self._source_keys(supporting_chunk)
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            if metadata.get("type") != "metadata_lookup":
                continue
            if supporting_sources & self._source_keys(chunk):
                return index, chunk
        return None

    @staticmethod
    def _supporting_sentence(question: str, chunk: dict[str, Any]) -> str:
        text = re.sub(r"\s+", " ", str(chunk.get("text", ""))).strip()
        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
        if not sentences:
            return text
        terms = {
            token
            for token in re.findall(r"[a-z0-9]+", question.lower())
            if len(token) > 2 and token not in {"which", "what", "company", "companies", "the", "did", "does"}
        }
        equivalents = {
            "buyback": {"repurchase", "repurchases", "repurchasing"},
            "share": {"share", "shares", "common stock"},
            "announced": {"announced", "approved", "authorized"},
        }

        def score(sentence: str) -> int:
            lowered = sentence.lower()
            direct = sum(1 for term in terms if term in lowered)
            related = sum(1 for term, values in equivalents.items() if term in terms and any(value in lowered for value in values))
            return direct + related

        return max(sentences, key=score)

    @staticmethod
    def _replace_generic_company(sentence: str, company_name: str) -> str:
        replaced = re.sub(r"\b[Tt]he Company\b", company_name, sentence, count=1)
        replaced = re.sub(r"\b[Tt]he Group\b", company_name, replaced, count=1)
        return replaced

    @staticmethod
    def _source_keys(chunk: dict[str, Any]) -> set[str]:
        metadata = chunk.get("metadata", {})
        values = [
            metadata.get("source_id"),
            metadata.get("sha1"),
            metadata.get("pdf_sha1"),
            metadata.get("document_id"),
            metadata.get("file_name"),
            metadata.get("source_path"),
            chunk.get("document_id"),
        ]
        keys = set()
        for value in values:
            if not value:
                continue
            raw = str(value)
            name = Path(raw).name
            stem = Path(name).stem if name else raw
            keys.update({raw, name, stem})
        return {key for key in keys if key}

    @staticmethod
    def _citation_label(index: int, chunk: dict[str, Any]) -> str:
        """Create a compact citation label for a retrieved chunk."""
        chunk_id = str(chunk.get("chunk_id", ""))[:8] or f"rank-{index}"
        if chunk.get("metadata", {}).get("type") == "metadata_lookup":
            metadata_id = str(chunk.get("metadata", {}).get("source_id") or chunk_id)[:8]
            return f"[metadata:{metadata_id}]"
        return f"[chunk:{index}:{chunk_id}]"
