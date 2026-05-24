"""Benchmark evaluation helpers."""

from src.eval.loaders import load_financebench, load_financebench_sample, load_hotpotqa
from src.eval.metrics import (
    boolean_accuracy_score,
    detect_abstention,
    evidence_recall_at_k,
    exact_match_score,
    f1_score,
    hit_at_k,
    mrr,
    numeric_match_score,
    retrieval_hit_at_k,
)
from src.eval.schema import QAExample

__all__ = [
    "QAExample",
    "boolean_accuracy_score",
    "detect_abstention",
    "evidence_recall_at_k",
    "exact_match_score",
    "f1_score",
    "hit_at_k",
    "load_financebench",
    "load_financebench_sample",
    "load_hotpotqa",
    "mrr",
    "numeric_match_score",
    "retrieval_hit_at_k",
]
