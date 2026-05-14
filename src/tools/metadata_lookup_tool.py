"""Metadata lookup tool for document/company identity."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

from src.tools.base import make_langchain_tool


LOGGER = logging.getLogger(__name__)


class MetadataLookupTool:
    """Lookup company metadata for RAG-Challenge document identifiers."""

    name = "lookup_document_metadata"
    description = "Lookup company metadata by PDF SHA1, document id, or source filename stem."

    def __init__(self, *, subset_csv: str | Path | None = None) -> None:
        self.subset_csv = Path(subset_csv) if subset_csv else None
        self.rows_by_id: dict[str, dict[str, str]] = {}
        self.available = False
        self._load()

    def run(self, *, source_ids: list[str] | None = None, source_id: str | None = None) -> dict[str, Any]:
        """Return metadata matches for source identifiers."""
        identifiers = list(source_ids or [])
        if source_id:
            identifiers.append(source_id)
        matches = []
        seen = set()
        for identifier in identifiers:
            normalized = self._normalize_identifier(identifier)
            row = self.rows_by_id.get(normalized)
            if not row:
                continue
            sha1 = row.get("sha1") or normalized
            if sha1 in seen:
                continue
            seen.add(sha1)
            matches.append(
                {
                    "source_id": identifier,
                    "matched_id": normalized,
                    "company_name": row.get("company_name"),
                    "metadata": dict(row),
                }
            )
        return {
            "available": self.available,
            "subset_csv": str(self.subset_csv) if self.subset_csv else None,
            "source_ids": identifiers,
            "matches": matches,
        }

    def as_langchain_tool(self) -> Any | None:
        """Return a LangChain-compatible tool when available."""
        return make_langchain_tool(self.name, self.description, self.run)

    def _load(self) -> None:
        if not self.subset_csv:
            LOGGER.warning("Metadata lookup disabled: no subset CSV configured.")
            return
        if not self.subset_csv.exists():
            LOGGER.warning("Metadata lookup disabled: subset CSV not found: %s", self.subset_csv)
            return

        with self.subset_csv.open("r", encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                ids = self._row_identifiers(row)
                for identifier in ids:
                    self.rows_by_id[identifier] = row
        self.available = bool(self.rows_by_id)
        LOGGER.info("Loaded metadata lookup rows from: %s", self.subset_csv)

    def _row_identifiers(self, row: dict[str, str]) -> set[str]:
        identifiers = set()
        for key in ("sha1", "pdf_sha1", "document_id", "doc_id", "company_id"):
            value = row.get(key)
            if value:
                identifiers.add(self._normalize_identifier(value))
        sha1 = row.get("sha1")
        if sha1:
            identifiers.add(self._normalize_identifier(f"{sha1}.pdf"))
        return {identifier for identifier in identifiers if identifier}

    @staticmethod
    def _normalize_identifier(identifier: object) -> str:
        path = Path(str(identifier or "").strip())
        name = path.name or str(identifier or "").strip()
        return path.stem if name.lower().endswith(".pdf") else name
