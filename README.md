# Agentic Enterprise RAG

This project studies when iterative evidence refinement helps enterprise RAG systems under noisy retrieval conditions.

It compares four QA settings:

| setting | behavior |
| --- | --- |
| `no_rag` | answer directly without retrieval |
| `basic_rag` | retrieve top-k chunks once, then answer |
| `reranker_rag` | retrieve a wider candidate set, rerank, then answer |
| `iterative_agentic_rag` | retrieve, detect evidence gaps, rewrite/retry when needed, then answer or abstain |

The core question is not whether retrieval helps in general. It does. The project focuses on the harder enterprise setting: noisy PDF chunks, ambiguous financial metrics, aliases, wrong-year distractors, multi-hop evidence, and unsupported questions where the system should refuse.

## System

```text
Question
  -> vector retrieval
  -> optional reranking
  -> evidence gap detection
  -> query rewrite + retry when evidence is weak
  -> grounded answer or abstention
```

Main components:

- PDF parsing and chunking with Docling.
- FAISS vector retrieval over persisted chunk indexes.
- Cross-encoder reranking with a lexical fallback.
- Evidence-aware agent loop with query rewriting, retry tracking, and refusal behavior.
- Benchmark runners for public datasets and a local enterprise PDF benchmark.

## Repository

```text
configs/       runtime config
data/          raw PDFs, processed chunks, vector indexes, eval JSONL
outputs/       benchmark outputs and summaries
scripts/       CLI entrypoints
src/
  agent/       planning, policy, evidence-gap logic
  eval/        benchmark loaders, metrics, agentic benchmark runner
  ingest/      Docling parsing and chunking
  indexing/    embeddings and vector-index persistence
  retrieval/   retriever and reranker
  tools/       retrieval, rerank, rewrite, answer, refusal tools
```

## Commands

Start vLLM API:

```bash
bash scripts/serve_qwen3_8b_vllm.sh
```

Run public benchmark evaluation:

```bash
python scripts/run_eval.py --dataset hotpotqa --setting basic_rag --max_examples 50
python scripts/run_eval.py --dataset financebench --setting iterative_agentic_rag --max_examples 50
```

Run enterprise PDF benchmark evaluation:

```bash
python scripts/run_eval.py \
  --dataset rag_challenge_test_set \
  --rag_challenge_path data/eval/rag_challenge_test_set.jsonl \
  --rag_challenge_index_dir data/processed/rag_challenge_test_index \
  --setting iterative_agentic_rag \
  --max_examples 100 \
  --max_iterations 2
```

Summarize results:

```bash
python scripts/summarize_results.py --input_dir outputs/eval_results_rag_challenge
```

## Public Benchmark Evaluation

Public benchmark runs use benchmark-native evidence mode:

- HotpotQA: dataset-provided context is used as the retrieval corpus.
- FinanceBench: dataset-provided evidence is used as the retrieval corpus.

This gives a constrained retrieval space. These runs are useful for standardized comparison, RAG vs. `no_rag`, reranking ablation, and evidence-aware abstention analysis. They are not raw-PDF retrieval experiments.

| dataset | setting | n | EM | F1 | numeric | boolean | hit | recall | MRR | abstain | retry | rewrite | gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| financebench | no_rag | 50 | 0.000 | 0.061 | 0.100 | 0.000 | 0.000 | 0.000 | 0.000 | 0.700 | 0.000 | 0.000 | 0.000 |
| financebench | basic_rag | 50 | 0.000 | 0.207 | 0.440 | 0.300 | 1.000 | 1.000 | 1.000 | 0.140 | 0.000 | 0.000 | 0.000 |
| financebench | reranker_rag | 50 | 0.000 | 0.208 | 0.440 | 0.300 | 1.000 | 1.000 | 1.000 | 0.160 | 0.000 | 0.000 | 0.000 |
| financebench | iterative_agentic_rag | 50 | 0.000 | 0.119 | 0.260 | 0.000 | 1.000 | 1.000 | 1.000 | 0.420 | 0.840 | 0.420 | 0.420 |
| hotpotqa | no_rag | 50 | 0.180 | 0.232 | 0.080 | 0.778 | 0.000 | 0.000 | 0.000 | 0.360 | 0.000 | 0.000 | 0.000 |
| hotpotqa | basic_rag | 50 | 0.500 | 0.559 | 0.140 | 0.889 | 1.000 | 0.848 | 0.886 | 0.220 | 0.000 | 0.000 | 0.000 |
| hotpotqa | reranker_rag | 50 | 0.480 | 0.565 | 0.140 | 0.889 | 1.000 | 0.809 | 0.857 | 0.160 | 0.000 | 0.000 | 0.000 |
| hotpotqa | iterative_agentic_rag | 50 | 0.480 | 0.539 | 0.140 | 0.778 | 1.000 | 0.848 | 0.886 | 0.240 | 0.420 | 0.340 | 0.340 |

Key observations:

- RAG substantially improves over `no_rag` on both datasets.
- Reranking gives modest gains or comparable performance.
- In benchmark-native evidence mode, retrieval is already constrained, so iterative refinement mainly demonstrates evidence-aware abstention, rewrite triggering, and retry behavior rather than dramatic retrieval gains.

Source: `outputs/eval_results_public/summary_table.csv` and matching `*_summary.json` files.

## Enterprise PDF Benchmark

The local enterprise benchmark, `rag_challenge_test_set`, is built from Docling-parsed PDFs, chunked enterprise documents, and a persisted FAISS vector index:

```text
data/raw_docs/rag_challenge_test_set/
data/processed/rag_challenge_test_index/
data/eval/rag_challenge_test_set.jsonl
```

Unlike the public benchmark setup, this benchmark uses true vector retrieval over a noisy PDF chunk corpus. Gold evidence is annotated by chunk id. The benchmark includes:

- alias and wording mismatch
- wrong-year and wrong-metric distractors
- evidence distributed across chunks/pages
- multi-hop questions
- OOD/refusal cases

Question categories are balanced across `fact_qa`, `numerical`, `multi_hop`, `boolean`, and `ood`.

| setting | n | EM | F1 | numeric | boolean | hit | recall | MRR | abstain | retry | rewrite | gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_rag | 100 | 0.000 | 0.074 | 0.020 | 0.000 | 0.000 | 0.000 | 0.000 | 0.800 | 0.000 | 0.000 | 0.000 |
| basic_rag | 100 | 0.060 | 0.274 | 0.180 | 0.000 | 0.800 | 0.800 | 0.788 | 0.510 | 0.000 | 0.000 | 0.000 |
| reranker_rag | 100 | 0.050 | 0.307 | 0.240 | 0.000 | 0.800 | 0.800 | 0.775 | 0.450 | 0.000 | 0.000 | 0.000 |
| iterative_agentic_rag | 100 | 0.260 | 0.377 | 0.170 | 0.000 | 0.800 | 0.800 | 0.788 | 0.520 | 0.800 | 0.600 | 0.600 |

In the noisy PDF setting, `iterative_agentic_rag` improves substantially over single-shot retrieval. The agent actively detects insufficient evidence, rewrites queries, and retries retrieval before answering. This is reflected in non-zero `avg_retry_count`, `rewrite_rate`, and `evidence_gap_rate`.

Source: `outputs/eval_results_rag_challenge/summary_table.csv` and matching `*_summary.json` files.

## Case Studies

These examples are selected from `outputs/eval_results_rag_challenge/rag_challenge_test_set_iterative_agentic_rag_20260524_105317.jsonl`.

### A. Multi-hop Retrieval Success

Question: Which acquisition expanded CrossFirst in 2022, and what adjusted diluted EPS and adjusted ROE did CrossFirst report for that year?

Why difficult: the answer requires linking acquisition evidence with separate performance metrics.

Rewrite example:

```text
Which acquisition expanded CrossFirst in 2022 ... e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf multi_hop hard
```

Evidence snippets:

- `bdabffc7...`, p.2: CrossFirst acquired Farmers & Stockmens Bank (`Central`) via merger.
- `be6c031...`, p.2: adjusted diluted EPS was `$1.37`; adjusted ROE improved to `11.11%`.

Why iterative helped: the initial evidence was incomplete, the agent marked an evidence gap, added document/category hints, and retrieved additional supporting chunks before answering.

### B. Reranker Failed, Iterative Succeeded

Question: Which product-service categories does Yellow Pages say the CEO reviews revenues by?

Gold answer: Print and Digital.

Reranker result: `Not sure.`

Iterative result: `Print and Digital.`

Rewrite example:

```text
Which product-service categories does Yellow Pages say the CEO reviews revenues by? 9d7a72445aba6860402c3acce75af02dc045f74d.pdf fact_qa medium revenue
```

Evidence snippet:

- `1902e614...`, p.51: the company reviews revenues by similar products and services, such as Print and Digital.

Why iterative helped: the single-shot setting missed or underused the relevant revenue-category evidence. The rewrite added document and metric hints, producing a more targeted retrieval round.

### C. OOD Abstention

Question: What was Apple's research and development expense in fiscal 2022?

Why difficult: the corpus contains a Holley R&D expense figure, which is a plausible but wrong-company distractor.

Retrieved distractor:

- `72cbb537...`, Holley p.37: research and development costs were `$29.1 million`.

Final answer:

```text
Not sure based on the provided documents.
```

Why iterative helped: the agent treated the retrieved evidence as insufficient for an Apple question, retried, and ultimately refused instead of copying a wrong-company metric.

## Interpretation

The public benchmark results show that retrieval and reranking improve standard QA metrics when evidence is already nearby. The enterprise PDF benchmark shows the more important behavior for production RAG: under noisy retrieval, iterative evidence refinement can improve answer quality and reduce unsupported answers by explicitly deciding when retrieved chunks are not enough.

The project does not claim state-of-the-art benchmark performance. It focuses on evaluation methodology, benchmark construction, retrieval robustness, and evidence-aware control flow for enterprise RAG.
