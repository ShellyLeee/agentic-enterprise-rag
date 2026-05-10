"""Docling-backed PDF parser adapter.

Docling is optional for the project skeleton. PDF ingestion requires it at
runtime; when Docling is missing or parsing fails, this module raises a clear
error instead of silently producing poor text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ingest.text_loader import compute_sha256, document_id_for_path
from src.schemas import Document, Page


class DoclingPdfParser:
    """Parse PDFs with Docling into canonical `Document` and `Page` objects."""

    def parse(self, source_path: str | Path) -> Document:
        """Parse a PDF file with Docling.

        Raises:
            RuntimeError: If Docling is unavailable or cannot parse the PDF.
            ValueError: If the input is not a PDF.
        """
        path = Path(source_path)
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"DoclingPdfParser only supports PDFs, got: {path.suffix}")

        try:
            from docling.document_converter import DocumentConverter
        except ImportError as exc:
            raise RuntimeError(
                "PDF parsing requires Docling. Install `docling` or ingest .txt/.md files instead."
            ) from exc

        try:
            converter = DocumentConverter()
            result = converter.convert(str(path))
            exported = result.document.export_to_dict()
        except Exception as exc:
            raise RuntimeError(f"Docling failed to parse PDF `{path}`: {exc}") from exc

        document_id = document_id_for_path(path)
        metadata = {
            "document_id": document_id,
            "source_path": str(path),
            "file_name": path.name,
            "file_type": "pdf",
        }
        pages = self._pages_from_docling_export(exported, metadata)

        if not pages:
            raise RuntimeError(f"Docling parsed `{path}` but produced no page text.")

        return Document(
            document_id=document_id,
            source_uri=str(path),
            title=path.stem,
            document_type="pdf",
            sha256=compute_sha256(path),
            pages=pages,
            metadata=metadata,
        )

    def _pages_from_docling_export(self, exported: dict[str, Any], metadata: dict[str, Any]) -> list[Page]:
        """Convert a Docling export dictionary into page records."""
        page_text: dict[int, list[str]] = {}

        for item in exported.get("texts", []):
            text = str(item.get("text") or "").strip()
            if not text:
                continue

            provenance = item.get("prov") or []
            page_number = 1
            if provenance:
                page_number = int(provenance[0].get("page_no") or 1)
            page_text.setdefault(page_number, []).append(text)

        return [
            Page(
                page_number=page_number,
                text="\n\n".join(blocks),
                metadata={**metadata, "page_number": page_number},
            )
            for page_number, blocks in sorted(page_text.items())
        ]

