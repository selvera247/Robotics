#!/usr/bin/env bash
# Shared constants and helpers for LeRobot environment setup.
# Sourced by scripts/setup_lerobot.sh — not meant to be run directly.
# shellcheck shell=bash

: "${ROOT:?ROOT must be set before sourcing lerobot_env.sh}"

LEROBOT_DIR="${ROOT}/lerobot"
LEROBOT_REPO_URL="${LEROBOT_REPO_URL:-https://github.com/huggingface/lerobot.git}"
# Feature extras for SO-101 / LeKiwi learning (sim-first). Keep in sync with README.
LEROBOT_EXTRAS="${LEROBOT_EXTRAS:-[core_scripts,training,feetech,lekiwi,pusht]}"
LEROBOT_PYTHON="${LEROBOT_PYTHON:-3.12}"

ensure_path_has_uv() {
  export PATH="${HOME}/.local/bin:${PATH}"
}

install_uv_if_needed() {
  ensure_path_has_uv
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  echo "==> Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # shellcheck disable=SC1091
  source "${HOME}/.local/bin/env"
}

install_ffmpeg_if_needed() {
  if command -v ffmpeg >/dev/null 2>&1; then
    return 0
  fi
  echo "==> Installing ffmpeg (video decoding for TorchCodec)"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg
  else
    echo "ffmpeg not found; install it for your OS, then re-run." >&2
    return 1
  fi
}

clone_lerobot_if_needed() {
  if [[ -d "${LEROBOT_DIR}/.git" ]]; then
    echo "==> Using existing clone at ${LEROBOT_DIR}"
    return 0
  fi
  echo "==> Cloning ${LEROBOT_REPO_URL}"
  git clone "${LEROBOT_REPO_URL}" "${LEROBOT_DIR}"
}

detect_torch_backend() {
  # CPU-only hosts must avoid default CUDA 13 Linux wheels (driver floor ≥ 580.65).
  if command -v nvidia-smi >/dev/null 2>&1; then
    echo "auto"
  else
    echo "cpu"
  fi
}

create_venv_if_needed() {
  cd "${LEROBOT_DIR}"
  if [[ -d .venv ]]; then
    return 0
  fi
  echo "==> Creating Python ${LEROBOT_PYTHON} venv"
  uv venv --python "${LEROBOT_PYTHON}" .venv
}

activate_lerobot_venv() {
  # shellcheck disable=SC1091
  source "${LEROBOT_DIR}/.venv/bin/activate"
}

install_pytorch() {
  local backend="$1"
  echo "==> Installing PyTorch (torch-backend=${backend})"
  uv pip install --torch-backend "${backend}" torch torchvision
}

install_lerobot_editable() {
  local extras_spec=".${LEROBOT_EXTRAS}"
  echo "==> Editable install ${extras_spec}"
  uv pip install -e "${extras_spec}"
}

verify_lerobot() {
  echo "==> Verifying with lerobot-info"
  lerobot-info
}

print_next_steps() {
  cat <<'EOF'

Setup complete.

  source lerobot/.venv/bin/activate
  cd lerobot

Sim-first next steps (also available as: python -m learning.smoke):

  python -m learning.smoke --dataset lerobot/pusht --episodes 0
  lerobot-dataset-viz --repo-id lerobot/pusht --episode-index 0
  lerobot-eval \
    --policy.path=lerobot/diffusion_pusht \
    --env.type=pusht \
    --eval.n_episodes=10 \
    --eval.batch_size=2 \
    --policy.device=cpu

Read AGENT_GUIDE.md before SO-101 / LeKiwi hardware steps:
  https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md
EOF
}
