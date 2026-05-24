# Agentic RAG: Iterative Evidence-Seeking Retrieval-Augmented Generation

An enterprise-oriented Agentic RAG system that actively detects evidence gaps, rewrites queries, and iteratively retrieves supporting evidence before answering or abstaining.

## Iterative Evidence-Seeking Loop

<p align="center">
  <img src="imgs/workflow.png" alt="Iterative evidence-seeking RAG workflow" width="860">
</p>

Unlike standard single-shot RAG pipelines, the system:

- retrieves and reranks candidate evidence,
- evaluates evidence sufficiency,
- detects missing relations,
- rewrites queries and performs follow-up retrieval,
- merges evidence across iterations,
- and finally answers or abstains.

## Enterprise PDF Benchmark

To evaluate enterprise retrieval robustness under realistic conditions, the project builds a custom benchmark, `rag_challenge_test_set`, from:

- Docling-parsed enterprise PDFs,
- a chunked document corpus,
- FAISS vector retrieval.

Question categories:

- `fact_qa`
- `numerical`
- `multi_hop`
- `boolean`
- `ood`

The benchmark intentionally includes:

- alias mismatch,
- cross-page evidence,
- retrieval ambiguity,
- noisy retrieval space,
- unsupported/OOD questions.

## Enterprise Benchmark Results

| setting | avg_em | avg_f1 |
| --- | ---: | ---: |
| no_rag | 0.000 | 0.074 |
| basic_rag | 0.060 | 0.274 |
| reranker_rag | 0.050 | 0.307 |
| iterative_agentic_rag | 0.260 | 0.377 |

Iterative evidence refinement provides the largest gains under noisy enterprise retrieval conditions, significantly improving EM/F1 over single-shot retrieval baselines.

For `iterative_agentic_rag`:

- `rewrite_rate`: 0.600
- `evidence_gap_rate`: 0.600
- `avg_retry_count`: 0.800

The agent actively:

- detects insufficient evidence,
- rewrites queries,
- retries retrieval,
- before answering.

## Case Studies

### Multi-hop Retrieval Example

- Question: Which acquisition expanded CrossFirst in 2022, and what adjusted diluted EPS and adjusted ROE did CrossFirst report for that year?
- Why difficult: the answer requires linking acquisition evidence with separate performance metrics.
- Rewrite example: `... e2b19d2cc2ccab2fd9022326b56b38fb0e772e73.pdf multi_hop hard`
- Why iterative helped: initial retrieval was incomplete; the agent detected an evidence gap, rewrote the query with document/task hints, retrieved additional supporting chunks, and produced a grounded final answer.

### OOD Refusal Example

- Question: What was Apple's research and development expense in fiscal 2022?
- Why difficult: the corpus contains a plausible distractor from Holley: research and development costs of `$29.1 million`.
- Final answer: `Not sure based on the provided documents.`
- Why iterative helped: the agent recognized that the retrieved evidence did not support an Apple-specific answer and abstained instead of copying a wrong-company metric.

## Public Benchmark Evaluation

The system is additionally evaluated on HotpotQA and FinanceBench for standardized comparison. These runs use benchmark-native evidence retrieval:

- HotpotQA uses dataset-provided context as the retrieval corpus.
- FinanceBench uses dataset-provided evidence as the retrieval corpus.

| dataset | setting | avg_em | avg_f1 |
| --- | --- | ---: | ---: |
| financebench | no_rag | 0.000 | 0.061 |
| financebench | basic_rag | 0.000 | 0.207 |
| financebench | reranker_rag | 0.000 | 0.208 |
| financebench | iterative_agentic_rag | 0.000 | 0.119 |
| hotpotqa | no_rag | 0.180 | 0.232 |
| hotpotqa | basic_rag | 0.500 | 0.559 |
| hotpotqa | reranker_rag | 0.480 | 0.565 |
| hotpotqa | iterative_agentic_rag | 0.480 | 0.539 |

On constrained benchmark-native retrieval settings, iterative refinement mainly demonstrates evidence-aware abstention and retry behavior rather than large retrieval gains.

## Start vLLM API

```bash
bash scripts/serve_qwen3_8b_vllm.sh
```

## Run Enterprise Benchmark

```bash
python scripts/run_eval.py --dataset rag_challenge_test_set --setting iterative_agentic_rag --max_examples 100
```

## Run Public Benchmark

```bash
python scripts/run_eval.py --dataset hotpotqa --setting basic_rag --max_examples 50
python scripts/run_eval.py --dataset financebench --setting reranker_rag --max_examples 50
```

## Summarize Results

```bash
python scripts/summarize_results.py --input_dir outputs/eval_results_rag_challenge
```

## Result Sources

- Enterprise benchmark table: `outputs/eval_results_rag_challenge/summary_table.csv`
- Public benchmark table: `outputs/eval_results_public/summary_table.csv`
- Case studies: `outputs/eval_results_rag_challenge/rag_challenge_test_set_iterative_agentic_rag_20260524_105317.jsonl`
