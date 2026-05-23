#!/usr/bin/env bash
set -euo pipefail

python -m vllm.entrypoints.openai.api_server \
  --model /data/common/LLMs/Qwen3-8B \
  --served-model-name qwen3-8b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 8192
