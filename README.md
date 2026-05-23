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
- Metadata lookup for document-to-company identity when source files use SHA-style names.
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
    ├── eval/            # HotpotQA/FinanceBench benchmark loaders and metrics
    ├── evaluation/      # Dataset loader, metrics, evaluator
    ├── generation/      # LLM client and answer generation
    ├── indexing/        # Embeddings and vector index persistence
    ├── ingest/          # PDF/text parsing and chunking
    ├── retrieval/       # Retriever and reranker
    ├── schemas/         # Pydantic data contracts
    └── tools/           # Retrieval, rerank, rewrite, answer, refusal tools
```

## Local LLM Serving with vLLM

The default real-LLM path uses a local vLLM OpenAI-compatible server for Qwen3-8B. The Agent process does not load model weights with `transformers.from_pretrained()`; it calls the API at `http://localhost:8000/v1`.

Install project dependencies:

```bash
pip install -r requirements.txt
```

Install vLLM in the serving environment. It is optional for clients, but required on the machine that hosts the local model:

```bash
pip install "vllm>=0.5"
```

Start the local Qwen3-8B API:

```bash
bash scripts/serve_qwen3_8b_vllm.sh
```

The script serves `/data/common/LLMs/Qwen3-8B` as model name `qwen3-8b` on port `8000`.

Test the API:

```bash
python scripts/test_llm_api.py
```

Equivalent direct API check:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EMPTY" \
  -d '{
    "model": "qwen3-8b",
    "messages": [{"role": "user", "content": "Who wrote the novel Pride and Prejudice?"}],
    "temperature": 0,
    "max_tokens": 64
  }'
```

Default Agent LLM config:

```yaml
llm:
  provider: openai_compatible
  base_url: http://localhost:8000/v1
  api_key: EMPTY
  model_name: qwen3-8b
```

Use `--mock` only when you explicitly want the deterministic smoke-test backend.

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

Run HotpotQA no-RAG benchmark evaluation:

```bash
python scripts/run_eval.py \
  --dataset hotpotqa \
  --max_examples 100 \
  --setting no_rag
```

Run HotpotQA RAG benchmark evaluation:

```bash
python scripts/run_eval.py \
  --dataset hotpotqa \
  --max_examples 100 \
  --setting rag \
  --top_k 5
```

Run FinanceBench sample RAG evaluation from HuggingFace:

```bash
python scripts/run_eval.py \
  --dataset financebench \
  --financebench_source hf \
  --max_examples 50 \
  --setting rag \
  --top_k 5
```

Benchmark outputs are written to `outputs/eval_results/{dataset}_{setting}_{timestamp}.jsonl` and a matching summary JSON. Each row includes `prediction`, EM/F1, retrieved docs, and retrieval hit.

FinanceBench sample can be loaded directly from HuggingFace:

```bash
python scripts/run_eval.py --dataset financebench --financebench_source hf --max_examples 50 --setting rag --top_k 5
```

The HuggingFace version contains 150 open-source sample examples. The full FinanceBench has 10,000+ examples and requires contacting the authors. Current evaluation uses the provided `evidence` field as the document corpus for benchmark-native RAG:

```text
question + provided evidence/context -> retrieval -> LLM answer -> EM/F1/retrieval hit
```

This stage does not download or parse original PDFs. A later document-level RAG mode can use `doc_link` PDFs with Docling parsing, chunking, retrieval, and LLM answering.

Local FinanceBench samples are still supported:

```bash
python scripts/run_eval.py \
  --dataset financebench \
  --financebench_source local \
  --financebench_local_path data/financebench/sample.jsonl \
  --max_examples 50 \
  --setting rag \
  --top_k 5
```

For local loading, place a JSON, JSONL, or CSV sample under `data/financebench/`, or pass a specific file with `--financebench_local_path`. The parser is intentionally permissive for public samples and hand-curated subsets. Large benchmark data and generated outputs are ignored by git.

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
