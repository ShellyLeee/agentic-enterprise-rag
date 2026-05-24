"""Prompt templates for benchmark QA settings."""

from __future__ import annotations

from src.eval.schema import QAExample


BASE_SYSTEM_PROMPT = (
    "You are a concise and reliable question-answering assistant. "
    "Do not output chain-of-thought, hidden reasoning, or <think> blocks. "
    "Only provide the final answer."
)


def system_prompt_for_setting(setting: str, example: QAExample, dataset_name: str) -> str:
    """Return a dataset- and setting-aware system prompt."""
    dataset = dataset_name.lower()
    parts = [BASE_SYSTEM_PROMPT]
    if setting == "no_rag":
        parts.append("Answer directly. If you are unsure, say: Not sure.")
    elif setting in {"basic_rag", "reranker_rag"}:
        parts.append(
            "Answer using only the provided context. Do not use unsupported facts. "
            "If the context is insufficient, say: Not sure. Keep the final answer concise."
        )
    elif setting == "agentic_rag_conservative":
        parts.append(
            "Use the context only if it strongly supports the answer. "
            "If evidence is weak, incomplete, or ambiguous, answer exactly: Not sure based on the provided context."
        )
    elif setting == "agentic_rag_balanced":
        parts.append(
            "Answer when the context is reasonably relevant and grounded. "
            "If the answer cannot be determined from the context, say: Not sure based on the provided context."
        )
    elif setting == "agentic_rag_aggressive":
        parts.append(
            "Synthesize across retrieved context and answer unless the context clearly cannot support the question. "
            "Stay concise and do not invent unsupported details."
        )

    if dataset == "financebench":
        parts.append(
            "For financial numerical questions, pay attention to units. If the question asks for USD millions, "
            "answer in USD millions. If it asks for USD billions, convert millions to billions. Preserve signs "
            "and percentages. Final answer format: Answer: ..."
        )
    elif dataset == "hotpotqa":
        parts.append(
            "For yes/no questions, the final answer should be exactly yes or no. "
            "For short-answer questions, answer with a short entity or phrase."
        )
    return " ".join(parts)


def user_prompt(question: str, context: str, setting: str) -> str:
    """Build the benchmark QA user prompt."""
    if setting == "no_rag":
        return f"""Question:
{question}

Answer:"""
    return f"""Question:
{question}

Context:
{context}

Answer:"""
