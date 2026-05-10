"""Offline ingestion pipeline for parsing documents and writing chunks."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from src.ingest.chunking import ChunkingConfig, DocumentChunker
from src.ingest.docling_parser import DoclingPdfParser
from src.ingest.text_loader import SUPPORTED_TEXT_SUFFIXES, TextDocumentLoader
from src.schemas import Chunk, Document


LOGGER = logging.getLogger(__name__)
SUPPORTED_SUFFIXES = SUPPORTED_TEXT_SUFFIXES | {".pdf"}


@dataclass(frozen=True)
class IngestionStats:
    """Summary counters emitted by the ingestion pipeline."""

    documents: int
    pages: int
    chunks: int
    output_path: Path


def load_ingestion_config(config_path: str | Path) -> ChunkingConfig:
    """Load chunking settings from a YAML config file."""
    path = Path(config_path)
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML config `{path}`: {exc}") from exc

    ingestion = config.get("ingestion", {})
    return ChunkingConfig(
        chunk_size=int(ingestion.get("chunk_size_tokens", 600)),
        chunk_overlap=int(ingestion.get("chunk_overlap_tokens", 80)),
    )


class IngestionPipeline:
    """Parse supported documents, normalize them, chunk them, and write JSONL."""

    def __init__(self, chunker: DocumentChunker) -> None:
        self.chunker = chunker
        self.text_loader = TextDocumentLoader()
        self.pdf_parser = DoclingPdfParser()

    def run(self, input_dir: str | Path, output_path: str | Path) -> IngestionStats:
        """Run ingestion for all supported files under an input directory."""
        input_path = Path(input_dir)
        output = Path(output_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_path}")
        if not input_path.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {input_path}")

        documents = list(self._load_documents(input_path))
        chunks = self._chunk_documents(documents)
        self._write_chunks(chunks, output)

        stats = IngestionStats(
            documents=len(documents),
            pages=sum(len(document.pages) for document in documents),
            chunks=len(chunks),
            output_path=output,
        )
        self._log_stats(stats)
        return stats

    def _load_documents(self, input_dir: Path) -> Iterable[Document]:
        """Load all supported documents from the input directory."""
        for path in sorted(input_dir.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue

            suffix = path.suffix.lower()
            if suffix not in SUPPORTED_SUFFIXES:
                LOGGER.debug("Skipping unsupported file: %s", path)
                continue

            LOGGER.info("Parsing %s", path)
            if suffix == ".pdf":
                yield self.pdf_parser.parse(path)
            else:
                yield self.text_loader.load(path)

    def _chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        """Split loaded documents into retrieval chunks."""
        chunks: list[Chunk] = []
        for document in documents:
            chunks.extend(self.chunker.split_document(document))
        return chunks

    def _write_chunks(self, chunks: list[Chunk], output_path: Path) -> None:
        """Write chunks to JSONL in Pydantic JSON mode."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            for chunk in chunks:
                file.write(json.dumps(chunk.model_dump(mode="json"), ensure_ascii=False) + "\n")

    def _log_stats(self, stats: IngestionStats) -> None:
        """Log ingestion summary counters."""
        LOGGER.info("Documents parsed: %s", stats.documents)
        LOGGER.info("Pages parsed: %s", stats.pages)
        LOGGER.info("Chunks created: %s", stats.chunks)
        LOGGER.info("Chunks written to: %s", stats.output_path)


def run_ingestion(
    input_dir: str | Path,
    output_path: str | Path,
    config_path: str | Path,
) -> IngestionStats:
    """Convenience function for scripts and tests."""
    chunk_config = load_ingestion_config(config_path)
    pipeline = IngestionPipeline(chunker=DocumentChunker(chunk_config))
    return pipeline.run(input_dir=input_dir, output_path=output_path)

