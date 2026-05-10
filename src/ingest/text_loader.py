"""Load plain-text enterprise documents into canonical document schemas."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from src.schemas import Document, Page


SUPPORTED_TEXT_SUFFIXES = {".md", ".txt"}


def compute_sha256(path: Path) -> str:
    """Compute a SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def document_id_for_path(path: Path) -> str:
    """Create a stable document ID from the absolute source path."""
    return hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()


def extract_title(text: str, fallback: str) -> str:
    """Extract a lightweight title from Markdown or plain text."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        markdown_heading = re.match(r"^#{1,6}\s+(.+)$", stripped)
        return markdown_heading.group(1).strip() if markdown_heading else stripped[:120]
    return fallback


class TextDocumentLoader:
    """Load `.txt` and `.md` files without requiring Docling."""

    def load(self, source_path: str | Path) -> Document:
        """Load a text document as a single-page canonical document."""
        path = Path(source_path)
        if path.suffix.lower() not in SUPPORTED_TEXT_SUFFIXES:
            raise ValueError(f"Unsupported text file type: {path.suffix}")

        text = path.read_text(encoding="utf-8")
        document_id = document_id_for_path(path)
        metadata = {
            "document_id": document_id,
            "source_path": str(path),
            "file_name": path.name,
            "file_type": path.suffix.lower().lstrip("."),
        }

        page = Page(
            page_number=1,
            text=text,
            metadata={
                **metadata,
                "page_number": 1,
            },
        )

        return Document(
            document_id=document_id,
            source_uri=str(path),
            title=extract_title(text, fallback=path.stem),
            document_type=path.suffix.lower().lstrip("."),
            sha256=compute_sha256(path),
            pages=[page],
            metadata=metadata,
        )

