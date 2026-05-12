#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$PROJECT_ROOT"

CONFIG_PATH="${CONFIG_PATH:-configs/default.yaml}"
RAW_DOCS_DIR="${RAW_DOCS_DIR:-data/raw_docs/rag_challenge_test_set}"
CHUNKS_PATH="${CHUNKS_PATH:-data/processed/rag_challenge_test_chunks.jsonl}"
INDEX_DIR="${INDEX_DIR:-data/processed/rag_challenge_test_index}"
QUESTIONS_PATH="${QUESTIONS_PATH:-data/external/rag_challenge_2/test_set/questions.json}"
ANSWERS_PATH="${ANSWERS_PATH:-data/external/rag_challenge_2/test_set/answers_max_nst_o3m.json}"
SUBSET_PATH="${SUBSET_PATH:-data/external/rag_challenge_2/test_set/subset.csv}"
EVAL_PATH="${EVAL_PATH:-data/eval/rag_challenge_test_set.jsonl}"
RESULTS_DIR="${RESULTS_DIR:-results/rag_challenge_test_eval}"
RAG_CHALLENGE_EVAL_MOCK="${RAG_CHALLENGE_EVAL_MOCK:-1}"

MOCK_ARGS=()
if [[ "$RAG_CHALLENGE_EVAL_MOCK" != "0" && "$RAG_CHALLENGE_EVAL_MOCK" != "false" ]]; then
  MOCK_ARGS=(--mock)
fi

mkdir -p "$(dirname "$CHUNKS_PATH")" "$INDEX_DIR" "$(dirname "$EVAL_PATH")" "$RESULTS_DIR"

echo "Project root: $PROJECT_ROOT"
echo "Config: $CONFIG_PATH"
echo "Mock evaluation: ${MOCK_ARGS[*]:-disabled}"

echo
echo "Step 1/4: parse RAG-Challenge-2 PDFs"
python scripts/parse_docs.py \
  --input_dir "$RAW_DOCS_DIR" \
  --output "$CHUNKS_PATH" \
  --config "$CONFIG_PATH"

echo
echo "Step 2/4: build vector index"
python scripts/build_index.py \
  --chunks "$CHUNKS_PATH" \
  --index_dir "$INDEX_DIR" \
  --config "$CONFIG_PATH"

echo
echo "Step 3/4: convert RAG-Challenge-2 test_set to eval JSONL"
python scripts/convert_rag_challenge_testset.py \
  --questions "$QUESTIONS_PATH" \
  --answers "$ANSWERS_PATH" \
  --subset "$SUBSET_PATH" \
  --output "$EVAL_PATH"

echo
echo "Step 4/4: run evaluation"
# Default Slurm jobs pass --mock through RAG_CHALLENGE_EVAL_MOCK=1 so retrieval,
# reranking, and policy behavior can be tested without LLM API dependence.
# To use a real LLM, export OPENAI_API_KEY and run with RAG_CHALLENGE_EVAL_MOCK=0.
python scripts/run_eval.py \
  --eval_file "$EVAL_PATH" \
  --methods naive,rerank,agentic \
  --agent_policies conservative,balanced,aggressive \
  --index_dir "$INDEX_DIR" \
  --config "$CONFIG_PATH" \
  "${MOCK_ARGS[@]}" \
  --output_dir "$RESULTS_DIR"

echo
echo "RAG-Challenge-2 evaluation pipeline complete."
echo "Chunks: $CHUNKS_PATH"
echo "Index: $INDEX_DIR"
echo "Eval JSONL: $EVAL_PATH"
echo "Results: $RESULTS_DIR"
