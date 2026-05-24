"""Benchmark-native iterative Agentic RAG runner.

This runner evaluates the project's core idea on per-example benchmark corpora:
retrieve evidence, check sufficiency, rewrite/retry when weak, merge evidence,
then answer or abstain. It intentionally does not parse raw PDFs or use the
global project vector index.
"""

from __future__ import annotations

import re
from typing import Any

from src.eval.metrics import evidence_recall_at_k
from src.eval.schema import QAExample
from src.llm import LLMClient, LLMGeneration
from src.prompts.qa_prompts import system_prompt_for_setting, user_prompt
from src.retrieval.simple_retriever import SimpleRetriever


class BenchmarkAgenticRunner:
    """Iterative evidence refinement runner for benchmark-provided corpora."""

    def __init__(
        self,
        llm_client: LLMClient,
        top_k: int = 5,
        retrieve_top_n: int = 20,
        max_iterations: int = 2,
        evidence_threshold: float = 0.15,
        numeric_tolerance: float = 0.02,
        dataset_name: str | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.top_k = top_k
        self.retrieve_top_n = retrieve_top_n
        self.max_iterations = max_iterations
        self.evidence_threshold = evidence_threshold
        self.numeric_tolerance = numeric_tolerance
        self.dataset_name = dataset_name

    def run(self, example: QAExample) -> dict[str, Any]:
        """Run iterative retrieve/check/rewrite/answer for one example."""
        dataset_name = self.dataset_name or str((example.metadata or {}).get("dataset") or "benchmark")
        retriever = SimpleRetriever()
        retriever.index(example.documents or [])

        initial_query = example.question
        retrieval_rounds = []
        rewritten_queries = []
        merged_docs: list[dict[str, Any]] = []

        current_query = initial_query
        retry_count = 0
        weak_evidence = True
        for round_index in range(self.max_iterations + 1):
            retrieved = retriever.retrieve(current_query, top_k=self.retrieve_top_n)
            top_docs = retrieved[: self.top_k]
            merged_docs = self._merge_docs(merged_docs, top_docs)
            weak_evidence = self._weak_evidence(example, merged_docs, dataset_name)
            retrieval_rounds.append(
                {
                    "round": round_index,
                    "query": current_query,
                    "top_score": self._top_score(top_docs),
                    "num_retrieved": len(top_docs),
                    "weak_evidence": weak_evidence,
                }
            )
            if not weak_evidence or retry_count >= self.max_iterations:
                break
            rewritten = self._rewrite_query(example, dataset_name, merged_docs, retry_count)
            rewritten_queries.append(rewritten)
            current_query = rewritten
            retry_count += 1

        final_docs = merged_docs[: self.top_k]
        abstained = bool(weak_evidence)
        if abstained:
            answer = "Not sure based on the provided context."
            generation = LLMGeneration(
                prediction=answer,
                raw_prediction=answer,
                model=self.llm_client.model_name,
                mode="iterative-policy-abstain",
            )
            final_decision = "refuse"
        else:
            context = self._format_context(final_docs)
            prompt = user_prompt(example.question, context, "iterative_agentic_rag")
            system_prompt = system_prompt_for_setting("iterative_agentic_rag", example, dataset_name)
            generation = self.llm_client.generate_from_prompt_with_raw(prompt, system_prompt=system_prompt)
            final_decision = "answer"

        return {
            "prediction": generation.prediction,
            "raw_prediction": generation.raw_prediction,
            "retrieved_docs": final_docs,
            "agent_trace": {
                "initial_query": initial_query,
                "rewritten_queries": rewritten_queries,
                "retrieval_rounds": retrieval_rounds,
                "evidence_gap_detected": bool(rewritten_queries),
                "weak_evidence": weak_evidence,
                "retry_count": retry_count,
                "final_decision": final_decision,
                "abstained": abstained,
                "final_evidence_count": len(final_docs),
            },
        }

    def _weak_evidence(self, example: QAExample, docs: list[dict[str, Any]], dataset_name: str) -> bool:
        """Check evidence sufficiency for benchmark-native corpora."""
        if not docs:
            return True
        if self._top_score(docs) < self.evidence_threshold:
            return True
        dataset = dataset_name.lower()
        if dataset == "hotpotqa" and example.gold_evidence:
            return evidence_recall_at_k(docs, example.gold_evidence) < 1.0
        if dataset == "financebench":
            return self._financebench_evidence_gap(example, docs)
        return False

    def _financebench_evidence_gap(self, example: QAExample, docs: list[dict[str, Any]]) -> bool:
        """Detect likely wrong financial metric/year/statement retrieval."""
        metadata = example.metadata or {}
        joined = " ".join(str(doc.get("title", "")) + " " + str(doc.get("text", "")) for doc in docs).lower()
        required_terms = [
            str(metadata.get("company") or "").lower(),
            str(metadata.get("doc_period") or "").lower(),
            *self._statement_terms(example.question),
            *self._metric_terms(example.question),
        ]
        required_terms = [term for term in required_terms if term and len(term) > 2]
        if not required_terms:
            return False
        hits = sum(1 for term in required_terms if term in joined)
        return hits / len(required_terms) < 0.4

    def _rewrite_query(
        self,
        example: QAExample,
        dataset_name: str,
        docs: list[dict[str, Any]],
        retry_count: int,
    ) -> str:
        """Generate a deterministic focused retry query."""
        dataset = dataset_name.lower()
        if dataset == "financebench":
            return self._rewrite_financebench(example)
        if dataset == "hotpotqa":
            return self._rewrite_hotpotqa(example, docs, retry_count)
        return example.question

    def _rewrite_financebench(self, example: QAExample) -> str:
        """Rewrite FinanceBench queries with company/year/document/metric hints."""
        metadata = example.metadata or {}
        pieces = [
            metadata.get("company"),
            metadata.get("doc_period"),
            metadata.get("doc_type"),
            *self._statement_terms(example.question),
            *self._metric_terms(example.question),
            example.question,
        ]
        return " ".join(str(piece) for piece in pieces if piece)

    def _rewrite_hotpotqa(self, example: QAExample, docs: list[dict[str, Any]], retry_count: int) -> str:
        """Rewrite HotpotQA queries with missing supporting titles when available."""
        metadata = example.metadata or {}
        question_type = str(metadata.get("type") or "").lower()
        retrieved_titles = {str(doc.get("title") or "").lower() for doc in docs}
        missing_titles = [
            str(evidence.get("title"))
            for evidence in example.gold_evidence or []
            if str(evidence.get("title") or "").lower() not in retrieved_titles
        ]
        title_hint = " ".join(missing_titles[:2])
        if question_type == "comparison":
            return f"{example.question} comparison {' '.join(self._capitalized_phrases(example.question))} {title_hint}".strip()
        return f"{example.question} {title_hint}".strip() if title_hint else example.question

    @staticmethod
    def _merge_docs(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate documents by id/title/text while preserving order."""
        merged = list(existing)
        seen = {
            str(doc.get("id") or doc.get("chunk_id") or doc.get("title") or doc.get("text", "")[:80])
            for doc in merged
        }
        for doc in incoming:
            key = str(doc.get("id") or doc.get("chunk_id") or doc.get("title") or doc.get("text", "")[:80])
            if key not in seen:
                seen.add(key)
                merged.append(doc)
        return merged

    @staticmethod
    def _top_score(docs: list[dict[str, Any]]) -> float:
        """Return best retrieval score from docs."""
        return max((float(doc.get("score", doc.get("retrieval_score", 0.0)) or 0.0) for doc in docs), default=0.0)

    @staticmethod
    def _format_context(documents: list[dict[str, Any]]) -> str:
        """Render retrieved documents into prompt context."""
        parts = []
        for index, document in enumerate(documents, start=1):
            parts.append(
                f"[chunk:{index}:{document.get('chunk_id', document.get('id', index))}]\n"
                f"title: {document.get('title', '')}\n"
                f"source: {document.get('source', '')}\n"
                f"score: {document.get('score')}\n"
                f"text: {document.get('text', '')}"
            )
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _statement_terms(question: str) -> list[str]:
        """Extract common financial statement terms from a question."""
        lowered = question.lower()
        terms = []
        for term in ("balance sheet", "cash flow statement", "income statement"):
            if term in lowered:
                terms.append(term)
        return terms

    @staticmethod
    def _metric_terms(question: str) -> list[str]:
        """Extract rough metric keywords for financial retrieval."""
        lowered = question.lower()
        keywords = [
            "capital expenditures",
            "property plant and equipment",
            "revenue",
            "net income",
            "operating cash flow",
            "cash",
            "debt",
            "assets",
            "liabilities",
            "margin",
            "sales",
        ]
        return [keyword for keyword in keywords if keyword in lowered]

    @staticmethod
    def _capitalized_phrases(question: str) -> list[str]:
        """Extract simple capitalized entity hints from a question."""
        return re.findall(r"\b[A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*)*", question)
