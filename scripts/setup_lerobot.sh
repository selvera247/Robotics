#!/usr/bin/env bash
# Reproducible LeRobot setup for this Robotics learning repo.
# Official docs: https://huggingface.co/docs/lerobot/installation
# Agent guide:   https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEROBOT_DIR="${ROOT}/lerobot"
EXTRAS='.[core_scripts,training,feetech,lekiwi,pusht]'

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  echo "==> Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  source "${HOME}/.local/bin/env"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "==> Installing ffmpeg (video decoding for TorchCodec)"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg
  else
    echo "ffmpeg not found; install it for your OS, then re-run." >&2
    exit 1
  fi
fi

if [[ ! -d "${LEROBOT_DIR}/.git" ]]; then
  echo "==> Cloning huggingface/lerobot"
  git clone https://github.com/huggingface/lerobot.git "${LEROBOT_DIR}"
else
  echo "==> Using existing clone at ${LEROBOT_DIR}"
fi

cd "${LEROBOT_DIR}"

if [[ ! -d .venv ]]; then
  echo "==> Creating Python 3.12 venv"
  uv venv --python 3.12 .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# CPU-only hosts must avoid default CUDA 13 Linux wheels (need driver ≥ 580.65).
TORCH_BACKEND="auto"
if ! command -v nvidia-smi >/dev/null 2>&1; then
  TORCH_BACKEND="cpu"
  echo "==> No NVIDIA GPU detected — installing CPU PyTorch"
else
  echo "==> NVIDIA GPU detected — using default PyTorch wheels"
fi

echo "==> Installing PyTorch (${TORCH_BACKEND})"
uv pip install --torch-backend "${TORCH_BACKEND}" torch torchvision

echo "==> Editable install ${EXTRAS}"
uv pip install -e "${EXTRAS}"

echo "==> Verifying with lerobot-info"
lerobot-info

cat <<'EOF'

Setup complete.

  source lerobot/.venv/bin/activate
  cd lerobot

Next (simulation-first, no hardware):

  python -c "from lerobot.datasets.lerobot_dataset import LeRobotDataset; ds = LeRobotDataset('lerobot/pusht', episodes=[0]); print(ds.repo_id, len(ds))"
  lerobot-dataset-viz --repo-id lerobot/pusht --episode-index 0
  lerobot-eval --policy.path=lerobot/diffusion_pusht --env.type=pusht --eval.n_episodes=10 --eval.batch_size=2 --policy.device=cpu

Read AGENT_GUIDE.md before SO-101 / LeKiwi hardware steps:
  https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md
EOF
