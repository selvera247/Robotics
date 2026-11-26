# HF Jobs runbook — Train ACT on PushT

CPU-only machines should not train policies locally ([hardware guide](https://huggingface.co/docs/lerobot/hardware_guide)). Use [Hugging Face Jobs](https://huggingface.co/docs/hub/jobs) via `--job.target` on `lerobot-train`, then re-eval on this box with `--policy.device=cpu`.

This is the same **train → eval** shape we will reuse for Lego-sorting demos (Hub dataset → ACT → `lerobot-eval` / later SO-101 rollout). See [AGENT_GUIDE.md](https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md) §4.9, §6–§7 and [il_robots](https://huggingface.co/docs/lerobot/il_robots#train-using-hugging-face-jobs).

## Prerequisites

- LeRobot env set up (`bash scripts/setup_lerobot.sh`; venv activated)
- Hugging Face account with Jobs access
- One-time auth: `hf auth login`
- List flavors/pricing: `hf jobs hardware`

## Dataset scale (for step counts)

`lerobot/pusht`: **206 episodes**, **25 650 frames**, 10 Hz.

At `--batch_size=8`:

- ~3 206 steps / epoch  
- ~5 epochs ≈ **16k steps** → this runbook uses `--steps=20000`

## Train (HF Jobs)

```bash
hf auth login
hf jobs hardware   # confirm t4-small / a10g-small availability

HF_USER=$(NO_COLOR=1 hf auth whoami | awk -F': *' 'NR==1 {print $2}')

source lerobot/.venv/bin/activate
cd lerobot

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

Notes:

- Prefer `--job.target=t4-small` for ACT (cheapest ACT-capable flavor). If missing from `hf jobs hardware`, use `a10g-small`.
- Logs stream to the terminal; **Ctrl-C detaches** — the job keeps running in the cloud.
- Remote Trackio **requires** `--trackio.space_id=…` (pod-local DB is lost when the job ends).
- Checkpoint lands on the Hub at `${HF_USER}/act_pusht_learn` when the job finishes pushing.

Job helpers (after submit):

```bash
hf jobs ps
hf jobs logs <job-id>
hf jobs cancel <job-id>
```

## Learning run (smaller / cheaper)

Same **train → eval** shape as above (and as later Lego demos) — just fewer steps (~2–3 epochs on PushT) to verify Jobs + ACT before a full 20k run.

```bash
hf auth login
HF_USER=$(NO_COLOR=1 hf auth whoami | awk -F': *' 'NR==1 {print $2}')
source lerobot/.venv/bin/activate && cd lerobot

lerobot-train \
  --dataset.repo_id=lerobot/pusht \
  --policy.type=act \
  --policy.device=cuda \
  --batch_size=8 \
  --steps=8000 \
  --save_freq=4000 \
  --log_freq=200 \
  --output_dir=outputs/train/act_pusht_learn_small \
  --job_name=act_pusht_learn_small \
  --policy.repo_id=${HF_USER}/act_pusht_learn_small \
  --job.target=t4-small \
  --job.timeout=2h \
  --trackio.enable=true \
  --trackio.space_id=${HF_USER}/lerobot-trackio
```

Rough cost (from `hf jobs hardware`; wall clock includes image pull + dataset download, not pure step time):

| Flavor | $/hour | Likely wall for 8k steps | Est. cost |
| --- | --- | --- | --- |
| `t4-small` | $0.40 | ~20–45 min | ~$0.15–$0.30 |
| `a10g-small` | $1.00 | ~15–35 min | ~$0.25–$0.60 |

Prefer `t4-small` for learning. After the job, eval with the CPU command below, swapping `act_pusht_learn` → `act_pusht_learn_small`. Expect lower success than a full 20k run; the goal is path familiarity.

## Eval locally (CPU)

After the Hub model exists:

```bash
source lerobot/.venv/bin/activate
cd lerobot

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

Outputs: `outputs/eval/act_pusht_own/` (metrics JSON, `eval.log`, per-episode MP4s under `videos/`).

### Success criteria

- Job completes without error; model repo visible on your HF profile  
- Local eval finishes cleanly; **success rate > 0%** (ideally well above the community ACT smoke we ran earlier)  
- You can explain: dataset keys → ACT → `--env.type=pusht` → videos/metrics

## Resume / longer train (optional)

```bash
lerobot-train \
  --config_path=${HF_USER}/act_pusht_learn \
  --resume=true \
  --job.target=t4-small \
  --job.timeout=4h
```

## Toward Lego sorting

Replace `lerobot/pusht` with your Hub demo dataset, keep `--policy.type=act`, then eval (sim or, later, SO-101 `lerobot-rollout`). Same CLI shape — only `repo_id`, cameras/state keys, and success definition change.
