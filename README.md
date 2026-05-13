# Agent-driven Enterprise RAG System (Agentic RAG)

An experimental Enterprise RAG system that compares three retrieval-augmented question-answering patterns:

- **Naive RAG**: retrieve chunks, then answer.
- **RAG + Reranker**: retrieve a wider set, rerank evidence, then answer.
- **Agentic RAG**: plan, retrieve, rerank, evaluate evidence quality, optionally rewrite the query, then answer or refuse.

The project is built to be runnable in local development environments. It prefers production-style components such as sentence-transformers embeddings, FAISS, and cross-encoder reranking, but includes lightweight fallback backends so the full pipeline can still run without model downloads or API keys.

## Motivation

Naive RAG is easy to build, but it often answers from noisy retrieval results. A fixed reranking pipeline can improve relevance, but it still lacks a decision layer: it will usually answer even when evidence is weak or out of scope.

This project adds an evidence-aware Agent workflow. The agent makes explicit decisions about whether evidence is strong enough to answer, whether a query should be rewritten and retried, or whether the system should refuse because the available documents do not support an answer.

## System Overview

```text
User Query
  ↓
Planner
  ↓
Retrieval Tool
  ↓
Rerank Tool
  ↓
Evidence Gap Detector
   ├── answer-ready evidence
   └── follow-up retrieval for missing fields
  ↓
Evidence-aware Policy
   ├── answer
   ├── rewrite query and retry
   └── refuse
  ↓
Answer Tool / Refusal Tool
```

Core capabilities:

- LangChain-compatible tool wrappers with direct Python-callable interfaces.
- FAISS vector indexing when available, with a NumPy cosine fallback.
- Sentence-transformers embeddings when available, with a deterministic hashing fallback.
- Cross-encoder reranking when available, with a deterministic lexical fallback.
- Query rewriting for weak evidence retries.
- Iterative evidence-seeking follow-up retrieval when top evidence is incomplete.
- Grounded refusal when the document set does not support an answer.
- Trace logging for agent decisions, retrieval results, reranking scores, policy statistics, and final output.

## Repository Structure

```text
agentic-enterprise-rag/
├── configs/             # Runtime config and agent policy presets
├── data/
│   ├── raw_docs/        # Source documents
│   ├── processed/       # Chunks and vector index artifacts
│   └── eval/            # Example evaluation JSONL
├── docs/                # Architecture notes and future evaluation plan
├── results/             # Traces and evaluation outputs
├── scripts/             # CLI entrypoints
└── src/
    ├── agent/           # Planner, evidence policy, executor, trace logger
    ├── evaluation/      # Dataset loader, metrics, evaluator
    ├── generation/      # LLM client and answer generation
    ├── indexing/        # Embeddings and vector index persistence
    ├── ingest/          # PDF/text parsing and chunking
    ├── retrieval/       # Retriever and reranker
    ├── schemas/         # Pydantic data contracts
    └── tools/           # Retrieval, rerank, rewrite, answer, refusal tools
```

## Quick Start

Install dependencies. The project can run in fallback mode even if optional FAISS or sentence-transformers downloads are unavailable.

```bash
pip install -r requirements.txt
```

Parse sample documents:

```bash
python scripts/parse_docs.py \
  --input_dir data/raw_docs \
  --output data/processed/chunks.jsonl \
  --config configs/default.yaml
```

Build a vector index:

```bash
python scripts/build_index.py \
  --chunks data/processed/chunks.jsonl \
  --index_dir data/processed/vector_index \
  --config configs/default.yaml
```

Run Naive RAG:

```bash
python scripts/run_naive_rag.py \
  --question "How many vacation days do new employees accrue?" \
  --top_k 5 \
  --index_dir data/processed/vector_index \
  --config configs/default.yaml \
  --mock
```

Run RAG + Reranker:

```bash
python scripts/run_rerank_rag.py \
  --question "How many vacation days do new employees accrue?" \
  --retrieve_k 10 \
  --rerank_top_n 5 \
  --index_dir data/processed/vector_index \
  --config configs/default.yaml \
  --mock
```

Run Agentic RAG:

```bash
python scripts/run_agentic_rag.py \
  --question "How many vacation days do new employees accrue?" \
  --index_dir data/processed/vector_index \
  --config configs/default.yaml \
  --agent_policy balanced \
  --mock \
  --save_trace results/agent_trace_sample.json
```

Run evaluation:

```bash
python scripts/run_eval.py \
  --eval_file data/eval/eval_questions.example.jsonl \
  --methods naive,rerank,agentic \
  --agent_policies conservative,balanced,aggressive \
  --index_dir data/processed/vector_index \
  --config configs/default.yaml \
  --mock \
  --output_dir results/eval_policy_sweep
```

Convert the local RAG-Challenge-2 test set to the same eval JSONL schema:

```bash
python scripts/convert_rag_challenge_testset.py \
  --questions data/external/rag_challenge_2/test_set/questions.json \
  --answers data/external/rag_challenge_2/test_set/answers_max_nst_o3m.json \
  --subset data/external/rag_challenge_2/test_set/subset.csv \
  --output data/eval/rag_challenge_test_set.jsonl
```

Run the full local RAG-Challenge-2 pipeline:

```bash
scripts/run_rag_challenge_pipeline.sh
```

## Slurm: RAG-Challenge-2 Test Set

The Slurm launchers activate the `agent_env` conda environment, parse PDFs from
`data/raw_docs/rag_challenge_test_set`, build `data/processed/rag_challenge_test_index`,
convert the test questions, and write evaluation outputs to `results/rag_challenge_test_eval`.

```bash
chmod +x scripts/run_rag_challenge_pipeline.sh scripts/slurm/*.sbatch

# GPU default: partition 4090, gpu:1, 8 CPUs, 48G, 4 hours.
sbatch scripts/slurm/run_rag_challenge_eval.sbatch

# CPU fallback: 8 CPUs, 48G, 6 hours.
sbatch scripts/slurm/run_rag_challenge_eval_cpu.sbatch
```

Both Slurm scripts keep `--mock` enabled by default so retrieval, reranking, and
policy behavior can be evaluated without an LLM API key. To use a real LLM:

```bash
export OPENAI_API_KEY=...
RAG_CHALLENGE_EVAL_MOCK=0 sbatch --export=ALL scripts/slurm/run_rag_challenge_eval.sbatch
```

## Example Outputs

Grounded answer:

```text
Question
How many vacation days do new employees accrue?

Answer
New employees accrue 15 vacation days per calendar year, prorated from their start date. [chunk:1:60968f54]
```

Out-of-domain refusal:

```text
Question
What is the company's policy on pet insurance?

Final Decision
refuse

Answer
I don't have enough grounded evidence to answer this question from the available documents.
```

## Smoke-test Evaluation

The current evaluation uses a tiny synthetic enterprise-policy dataset derived from `data/raw_docs/sample_policy.md`. These metrics validate pipeline behavior; they are **not benchmark results**.

The following table comes from mock mode with local fallback embeddings/reranking in this environment:

| method | overall_f1 | answerable_f1 | ood_refusal_accuracy | unsupported_rate |
| --- | ---: | ---: | ---: | ---: |
| naive | 0.256 | 0.318 | 0.000 | 0.200 |
| rerank | 0.263 | 0.318 | 0.000 | 0.200 |
| agentic_conservative | 0.058 | 0.027 | 1.000 | 0.000 |
| agentic_balanced | 0.195 | 0.199 | 1.000 | 0.000 |
| agentic_aggressive | 0.281 | 0.318 | 0.750 | 0.050 |

Interpretation:

- Naive and rerank baselines answer more often, but do not refuse OOD questions.
- Conservative and balanced agent policies protect against unsupported OOD answers, but over-refuse answerable questions.
- The aggressive policy improves answerable coverage on this smoke test, but allows one OOD false answer.
