# Robotics — LeRobot (SO-101 / LeKiwi) learning env

Simulation-first Hugging Face [LeRobot](https://github.com/huggingface/lerobot) setup for the SO-101 / LeKiwi ecosystem. **No robot hardware is required** for the steps below.

Official install guide: https://huggingface.co/docs/lerobot/installation  
Agent / learning companion: https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md  
Architecture notes: [`docs/architecture.md`](docs/architecture.md) · HF Jobs PushT: [`docs/hf_jobs_pusht.md`](docs/hf_jobs_pusht.md) · Cursor rules: [`.cursorrules`](.cursorrules)

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

## HF Jobs: Train ACT on PushT

This machine is CPU-only — **do not train locally**. Submit ACT training on [Hugging Face Jobs](https://huggingface.co/docs/hub/jobs), then eval the Hub checkpoint here with `--policy.device=cpu`. Full runbook: [`docs/hf_jobs_pusht.md`](docs/hf_jobs_pusht.md).

This is the same **train → eval** shape we’ll use later for Lego-sorting demos.

```bash
hf auth login
hf jobs hardware   # confirm t4-small / a10g-small

HF_USER=$(NO_COLOR=1 hf auth whoami | awk -F': *' 'NR==1 {print $2}')
source lerobot/.venv/bin/activate && cd lerobot

lerobot-train \
  --dataset.repo_id=lerobot/pusht \
  --policy.type=act \
  --policy.device=cuda \
  --batch_size=8 \
  --steps=20000 \
  --save_freq=5000 \
  --log_freq=200 \
  --output_dir=outputs/train/act_pusht_hfjob \
  --job_name=act_pusht_learn \
  --policy.repo_id=${HF_USER}/act_pusht_learn \
  --job.target=t4-small \
  --job.timeout=4h \
  --trackio.enable=true \
  --trackio.space_id=${HF_USER}/lerobot-trackio
```

If `t4-small` is unavailable, use `--job.target=a10g-small`. Ctrl-C detaches; the job keeps running.

**After the job finishes — eval on this CPU box:**

```bash
source lerobot/.venv/bin/activate && cd lerobot
HF_USER=$(NO_COLOR=1 hf auth whoami | awk -F': *' 'NR==1 {print $2}')

lerobot-eval \
  --policy.path=${HF_USER}/act_pusht_learn \
  --env.type=pusht \
  --eval.n_episodes=10 \
  --eval.batch_size=1 \
  --policy.device=cpu \
  --policy.dtype=float32 \
  --policy.use_amp=false \
  --output_dir=../outputs/eval/act_pusht_own
```

## Tests for this repo's helpers

```bash
source lerobot/.venv/bin/activate
PYTHONPATH=. python -m pytest learning/tests -q
```

## When you get SO-101 / LeKiwi hardware

Follow **Path A** in [`AGENT_GUIDE.md`](https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md): find port → setup motors → calibrate → teleoperate → record → train → rollout. Do not run those commands until arms are assembled and powered.
