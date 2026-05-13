"""Transparent heuristics for detecting incomplete evidence."""

from __future__ import annotations

import re
from typing import Any


COMPANY_SUFFIXES = (
    "Inc",
    "Inc.",
    "PLC",
    "Ltd",
    "Limited",
    "Corp",
    "Corporation",
    "Company",
    "Holdings",
    "Group",
    "Bank",
    "S.A.",
    "LLC",
)


class EvidenceGapDetector:
    """Detect missing fields that should trigger follow-up retrieval."""

    def __init__(self, *, min_gap_detection_score: float = 0.0) -> None:
        self.min_gap_detection_score = min_gap_detection_score

    def detect(self, question: str, evidence_chunks: list[dict[str, Any]], query_type: str) -> dict[str, Any]:
        """Return a transparent evidence-gap report for a question and top evidence."""
        normalized_question = question.lower()
        top_chunks = self._eligible_chunks(evidence_chunks)
        evidence_text = "\n".join(str(chunk.get("text", "")) for chunk in top_chunks)
        missing_fields: list[str] = []
        followup_queries: list[str] = []
        reasons: list[str] = []

        if self._asks_company(normalized_question) and self._missing_company_name(evidence_text):
            missing_fields.append("company_name")
            followup_queries.extend(self._company_followups(top_chunks))
            reasons.append("Question asks for a company, but top evidence does not contain a clear company name.")

        if self._asks_number(normalized_question) and not self._has_number(evidence_text):
            missing_fields.append("numeric_value")
            followup_queries.append(f"{question} numeric value amount percentage annual report")
            reasons.append("Question asks for a number, amount, or percentage, but top evidence has no numeric value.")

        if self._asks_date(normalized_question) and not self._has_date(evidence_text):
            missing_fields.append("date")
            followup_queries.append(f"{question} date year annual report")
            reasons.append("Question asks for a date or year, but top evidence has no date-like value.")

        if query_type == "comparison" and not self._has_enough_comparison_support(top_chunks, normalized_question):
            missing_fields.append("comparison_target")
            followup_queries.append(f"{question} comparison target annual report")
            reasons.append("Comparison-style question has evidence from fewer than two distinct targets, documents, sections, or pages.")

        if query_type == "multi_hop" and not self._has_enough_multi_hop_support(top_chunks):
            missing_fields.append("supporting_relation")
            followup_queries.append(f"{question} supporting evidence annual report")
            reasons.append("Multi-hop question has fewer than two distinct supporting chunks.")

        followup_queries = self._unique_strings(followup_queries)
        return {
            "has_gap": bool(missing_fields),
            "missing_fields": missing_fields,
            "followup_queries": followup_queries,
            "reason": " ".join(reasons) if reasons else "No obvious evidence gap detected.",
        }

    def _eligible_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self.min_gap_detection_score <= 0:
            return chunks
        eligible = [
            chunk
            for chunk in chunks
            if float(chunk.get("rerank_score", chunk.get("score", 0.0)) or 0.0) >= self.min_gap_detection_score
        ]
        return eligible or chunks

    @staticmethod
    def _asks_company(normalized_question: str) -> bool:
        return bool(re.search(r"\b(which|what)\s+compan(?:y|ies)\b", normalized_question))

    @staticmethod
    def _asks_number(normalized_question: str) -> bool:
        return bool(
            re.search(
                r"\b(how many|how much|amount|percentage|percent|%|margin|revenue|income|profit|usd|eur|gbp|number)\b",
                normalized_question,
            )
        )

    @staticmethod
    def _asks_date(normalized_question: str) -> bool:
        return bool(re.search(r"\b(when|date|year|period|latest|last period)\b", normalized_question))

    def _missing_company_name(self, evidence_text: str) -> bool:
        if not evidence_text.strip():
            return True
        return not self._has_company_name(evidence_text)

    @staticmethod
    def _has_company_name(text: str) -> bool:
        text = re.sub(r"\b(?:the|this|our)\s+(?:company|group)\b", "", text, flags=re.IGNORECASE)
        suffix_pattern = "|".join(re.escape(suffix) for suffix in COMPANY_SUFFIXES)
        return bool(re.search(rf"\b[A-Z][A-Za-z&.,'-]*(?:\s+[A-Z][A-Za-z&.,'-]*){{0,5}}\s+(?:{suffix_pattern})\b", text))

    @staticmethod
    def _has_number(text: str) -> bool:
        return bool(re.search(r"(?:[$€£¥]\s*)?\d[\d,]*(?:\.\d+)?\s*%?", text))

    @staticmethod
    def _has_date(text: str) -> bool:
        return bool(
            re.search(
                r"\b(?:19|20)\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\b",
                text,
                flags=re.IGNORECASE,
            )
        )

    def _has_enough_comparison_support(self, chunks: list[dict[str, Any]], normalized_question: str) -> bool:
        if self._asks_company(normalized_question):
            return True
        return len(self._distinct_evidence_keys(chunks)) >= 2

    def _has_enough_multi_hop_support(self, chunks: list[dict[str, Any]]) -> bool:
        return len(self._distinct_evidence_keys(chunks)) >= 2

    @staticmethod
    def _distinct_evidence_keys(chunks: list[dict[str, Any]]) -> set[str]:
        keys = set()
        for index, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source_path") or metadata.get("file_name") or metadata.get("document_id")
            page = metadata.get("page_number") or metadata.get("page_index")
            section = metadata.get("section_title")
            chunk_id = chunk.get("chunk_id")
            keys.add(str((source, page, section) if any((source, page, section)) else chunk_id or index))
        return keys

    @staticmethod
    def _company_followups(chunks: list[dict[str, Any]]) -> list[str]:
        queries = [
            "What company does this annual report belong to?",
            "company name annual report",
        ]
        source_names = []
        for chunk in chunks[:3]:
            metadata = chunk.get("metadata", {})
            source = metadata.get("file_name") or metadata.get("source_path")
            if source:
                source_names.append(str(source))
        for source_name in dict.fromkeys(source_names):
            queries.append(f"company name annual report {source_name}")
        return queries

    @staticmethod
    def _unique_strings(values: list[str]) -> list[str]:
        unique: list[str] = []
        for value in values:
            cleaned = re.sub(r"\s+", " ", value).strip()
            if cleaned and cleaned not in unique:
                unique.append(cleaned)
        return unique
