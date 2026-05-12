#!/usr/bin/env bash
#SBATCH --job-name=rag-challenge-eval
#SBATCH --output=logs/slurm/%x-%j.out
#SBATCH --error=logs/slurm/%x-%j.err
#
# Change this to your cluster's GPU partition if needed, for example: gpu.
#SBATCH --partition=4090
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_ROOT"
mkdir -p logs/slurm

CONDA_ENV_NAME="${CONDA_ENV_NAME:-agent_env}"
if command -v conda >/dev/null 2>&1; then
  eval "$(conda shell.bash hook)"
elif [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/anaconda3/etc/profile.d/conda.sh"
else
  echo "Could not find conda. Load your cluster's conda module or set up agent_env first." >&2
  exit 1
fi
conda activate "$CONDA_ENV_NAME"

echo "Job: ${SLURM_JOB_NAME:-local} ${SLURM_JOB_ID:-no-job-id}"
echo "Project root: $PROJECT_ROOT"
echo "Host: $(hostname)"
echo "Python path: $(command -v python)"
python - <<'PY'
import sys

print(f"Python executable: {sys.executable}")
try:
    import torch
except Exception as exc:
    print(f"CUDA availability: torch import failed ({exc})")
else:
    print(f"CUDA availability: {torch.cuda.is_available()}")
    print(f"CUDA device count: {torch.cuda.device_count()}")
    if torch.cuda.is_available():
        print(f"CUDA device 0: {torch.cuda.get_device_name(0)}")
PY

# Keep --mock by default for retrieval, reranking, and policy evaluation without
# OPENAI_API_KEY dependence. To use a real LLM, submit with:
#   export OPENAI_API_KEY=...
#   RAG_CHALLENGE_EVAL_MOCK=0 sbatch --export=ALL scripts/slurm/run_rag_challenge_eval.sbatch
export RAG_CHALLENGE_EVAL_MOCK="${RAG_CHALLENGE_EVAL_MOCK:-1}"

bash scripts/run_rag_challenge_pipeline.sh
