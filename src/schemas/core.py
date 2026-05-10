"""Canonical Pydantic schemas shared by ingestion, retrieval, agents, and evaluation.

The models in this module are intentionally compact. They define the stable
contracts the rest of the system will use while parsing, indexing, retrieving,
reasoning over evidence, validating citations, and evaluating answers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Metadata = dict[str, Any]


class Page(BaseModel):
    """A normalized page from an enterprise document."""

    page_id: str = Field(default_factory=lambda: str(uuid4()))
    page_number: int = Field(ge=1)
    text: str = ""
    metadata: Metadata = Field(default_factory=dict)


class Document(BaseModel):
    """A normalized source document before chunking and indexing."""

    document_id: str = Field(default_factory=lambda: str(uuid4()))
    source_uri: str
    title: str | None = None
    organization: str | None = None
    document_type: str | None = None
    sha256: str | None = None
    pages: list[Page] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)


class Chunk(BaseModel):
    """A retrieval unit derived from a page, table, or other document span."""

    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    parent_page_id: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    text: str
    token_count: int | None = Field(default=None, ge=0)
    chunk_type: Literal["text", "table", "figure", "appendix", "mixed"] = "text"
    metadata: Metadata = Field(default_factory=dict)


class Citation(BaseModel):
    """A source reference supporting an answer claim."""

    citation_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    page_number: int | None = Field(default=None, ge=1)
    chunk_id: str | None = None
    quote: str | None = None
    supports_claim: bool | None = None
    validation_notes: str | None = None
    metadata: Metadata = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """A retrieved evidence candidate before or after reranking."""

    chunk: Chunk
    score: float
    rank: int | None = Field(default=None, ge=1)
    retriever: str
    rerank_score: float | None = None
    parent_page: Page | None = None
    citations: list[Citation] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)


class Answer(BaseModel):
    """Structured answer returned by the evidence-aware agent."""

    question: str
    answer: str | int | float | bool | list[str] | None
    answer_type: Literal["string", "number", "boolean", "list", "unknown"] = "unknown"
    reasoning_summary: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    is_answered: bool = True
    validation_status: Literal["unvalidated", "supported", "unsupported", "partial"] = "unvalidated"
    metadata: Metadata = Field(default_factory=dict)


class AgentTrace(BaseModel):
    """Trace record for agent planning, tool use, evidence checks, and generation."""

    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    steps: list[Metadata] = Field(default_factory=list)
    retrieval_results: list[RetrievalResult] = Field(default_factory=list)
    answer: Answer | None = None
    errors: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)

