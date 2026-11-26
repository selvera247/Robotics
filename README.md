# Robotics — LeRobot (SO-101 / LeKiwi) learning env

Simulation-first Hugging Face [LeRobot](https://github.com/huggingface/lerobot) setup for the SO-101 / LeKiwi ecosystem. **No robot hardware is required** for the steps below.

Official install guide: https://huggingface.co/docs/lerobot/installation  
Agent / learning companion: https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md  
Architecture notes: [`docs/architecture.md`](docs/architecture.md) · Cursor rules: [`.cursorrules`](.cursorrules)

## What this environment includes

| Piece | Detail |
| --- | --- |
| Python | 3.12 via `uv` venv |
| Install | Editable `lerobot` with `core_scripts` + `training` + `feetech` + `lekiwi` + `pusht` |
| Video | System `ffmpeg` (TorchCodec) |
| Helpers | `learning/` package — typed smoke checks for env + Hub datasets |
| Hardware | Feetech / LeKiwi extras present for later — **not connected** |

## Setup (once)

Requires [uv](https://docs.astral.sh/uv/) and `ffmpeg` (`sudo apt install ffmpeg` on Ubuntu).

```bash
bash scripts/setup_lerobot.sh
```

That script (helpers in `scripts/lib/lerobot_env.sh`) will:

1. Install `uv` if needed  
2. Clone `https://github.com/huggingface/lerobot.git` into `./lerobot`  
3. Create a Python 3.12 venv  
4. Install CPU PyTorch when no NVIDIA GPU is detected (CUDA wheels otherwise)  
5. `uv pip install -e ".[core_scripts,training,feetech,lekiwi,pusht]"`  
6. Run `lerobot-info` to verify  

Activate in every new shell:

```bash
source lerobot/.venv/bin/activate
cd /path/to/this/repo   # repo root, so `learning` is importable
lerobot-info
```

### Conda (miniforge) alternative

If you prefer conda instead of uv (official docs default):

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
conda install ffmpeg -c conda-forge
git clone https://github.com/huggingface/lerobot.git && cd lerobot
pip install -e ".[core_scripts,training,feetech,lekiwi,pusht]"
lerobot-info
```

## Next commands (no hardware)

From the **repo root** with the venv active:

**1. Probe env + a public dataset** (preferred over ad-hoc one-liners)

```bash
python -m learning.smoke --dataset lerobot/pusht --episodes 0
```

**2. Visualize one episode** (opens Rerun)

```bash
lerobot-dataset-viz --repo-id lerobot/pusht --episode-index 0
```

**3. Run a short PushT simulation eval** (pretrained Hub policy; use `cpu` until you have CUDA)

```bash
lerobot-eval \
  --policy.path=lerobot/diffusion_pusht \
  --env.type=pusht \
  --eval.n_episodes=10 \
  --eval.batch_size=2 \
  --policy.device=cpu
```

Optional: browse more Hub datasets at https://huggingface.co/datasets?other=LeRobot or open https://huggingface.co/spaces/lerobot/visualize_dataset

## Tests for this repo's helpers

```bash
source lerobot/.venv/bin/activate
PYTHONPATH=. python -m pytest learning/tests -q
```

## When you get SO-101 / LeKiwi hardware

Follow **Path A** in [`AGENT_GUIDE.md`](https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md): find port → setup motors → calibrate → teleoperate → record → train → rollout. Do not run those commands until arms are assembled and powered.
