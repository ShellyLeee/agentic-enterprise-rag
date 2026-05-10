"""Chunk normalized documents for retrieval."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover - compatibility for older LangChain installs.
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.schemas import Chunk, Document, Page


def _stable_chunk_id(document_id: str, page_number: int, index: int, text: str) -> str:
    """Create a deterministic chunk ID from source location and content."""
    payload = f"{document_id}:{page_number}:{index}:{text}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def _nearest_section_title(page_text: str, chunk_text: str) -> str | None:
    """Find the closest Markdown-style section heading before a chunk."""
    start = page_text.find(chunk_text[:80])
    prefix = page_text[:start] if start >= 0 else page_text
    headings = re.findall(r"^#{1,6}\s+(.+)$", prefix, flags=re.MULTILINE)
    if headings:
        return headings[-1].strip()

    chunk_headings = re.findall(r"^#{2,6}\s+(.+)$", chunk_text, flags=re.MULTILINE)
    return chunk_headings[0].strip() if chunk_headings else None


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for token-aware chunking."""

    chunk_size: int = 600
    chunk_overlap: int = 80


class DocumentChunker:
    """Split documents into LangChain recursive-character chunks."""

    def __init__(self, config: ChunkingConfig) -> None:
        self.config = config
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

    def split_document(self, document: Document) -> list[Chunk]:
        """Split all pages in a document into canonical chunks."""
        chunks: list[Chunk] = []
        for page in document.pages:
            chunks.extend(self._split_page(document, page))
        return chunks

    def _split_page(self, document: Document, page: Page) -> list[Chunk]:
        """Split one page and preserve source metadata on each chunk."""
        pieces = self.splitter.split_text(page.text)
        chunks: list[Chunk] = []

        for index, text in enumerate(pieces):
            section_title = _nearest_section_title(page.text, text)
            chunk_id = _stable_chunk_id(document.document_id, page.page_number, index, text)
            metadata = {
                **document.metadata,
                **page.metadata,
                "document_id": document.document_id,
                "source_path": document.source_uri,
                "file_name": document.metadata.get("file_name"),
                "page_number": page.page_number,
                "section_title": section_title,
                "chunk_id": chunk_id,
                "chunk_index": index,
            }
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    parent_page_id=page.page_id,
                    page_number=page.page_number,
                    text=text,
                    token_count=None,
                    chunk_type="text",
                    metadata=metadata,
                )
            )

        return chunks
