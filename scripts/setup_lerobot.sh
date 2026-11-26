#!/usr/bin/env bash
# Reproducible LeRobot setup for this Robotics learning repo.
# Official docs: https://huggingface.co/docs/lerobot/installation
# Agent guide:   https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT}/scripts/lib/lerobot_env.sh"

install_uv_if_needed
install_ffmpeg_if_needed
clone_lerobot_if_needed
create_venv_if_needed
activate_lerobot_venv

TORCH_BACKEND="$(detect_torch_backend)"
if [[ "${TORCH_BACKEND}" == "cpu" ]]; then
  echo "==> No NVIDIA GPU detected — installing CPU PyTorch"
else
  echo "==> NVIDIA GPU detected — using default PyTorch wheels"
fi

install_pytorch "${TORCH_BACKEND}"
install_lerobot_editable
verify_lerobot
print_next_steps
