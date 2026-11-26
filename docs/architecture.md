# LeRobot architecture (learning notes)

Companion to upstream [`AGENTS.md`](https://github.com/huggingface/lerobot/blob/main/AGENTS.md) and [`AGENT_GUIDE.md`](https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md). This repo vendors LeRobot as a local clone under `./lerobot` (gitignored); treat that tree as the system under study.

## Mental model

LeRobot is four contracts glued by configs (draccus) and processors:

| Layer | Role | Key types / paths |
| --- | --- | --- |
| **Datasets** | Episode-aware Hub/disk storage + video decode | `LeRobotDataset` → `src/lerobot/datasets/` |
| **Policies** | Trainable `nn.Module`s with Hub push/pull | `PreTrainedPolicy` → `src/lerobot/policies/` |
| **Robots / teleops** | Real hardware I/O | `Robot`, `Teleoperator` → `robots/`, `teleoperators/`, `motors/`, `cameras/` |
| **Envs / sim** | Gymnasium benchmarks + sim-as-robot | `EnvConfig`, `SimRobot` → `envs/`, `sim/` |

Processors (`src/lerobot/processor/`) sit between dataset ↔ policy ↔ robot so feature names/shapes can be remapped without rewriting models.

## End-to-end data flows

```
Record:  teleop/policy → robot.get_observation/send_action → LeRobotDataset.create/writer → Hub
Train:   Hub dataset → DataLoader (+ processors) → policy.forward → checkpoint (+ optional Hub push)
Eval:    Hub/local policy → make_env(env.type) → lerobot-eval rollouts → success metrics
Rollout: Hub/local policy → real Robot (or SimRobot) → lerobot-rollout
```

CLI entrypoints are declared in `lerobot/pyproject.toml` `[project.scripts]` and implemented under `src/lerobot/scripts/`.

## SO-101 / LeKiwi specifics

- SO-100/101 share `SOFollower` / `SOLeader` bases with `@register_subclass("so100_*" | "so101_*")` aliases (`robots/so_follower`, `teleoperators/so_leader`).
- LeKiwi adds host/client ZMQ paths (`robots/lekiwi`) on top of Feetech motors (`extra: feetech`, `lekiwi`).
- Simulation-first learning should use Hub datasets (`lerobot/pusht`, …) and `lerobot-eval --env.type=pusht` before any USB/calibrate commands.

## Problem areas (upstream — do not fork lightly)

See the architecture canvas in this chat for prioritized findings. High-level themes:

1. **Factory sprawl** — `make_robot_from_config` still hand-lists many types despite a generic `make_device_from_device_class` fallback (explicit TODO in `robots/utils.py`).
2. **God modules** — several policy/processor/dataset files exceed 1.5–2.5k LOC; high change risk.
3. **Video I/O cost** — `datasets/video_utils.py` + TorchCodec/ffmpeg dominate dataloading; episode subsetting matters on CPU hosts.
4. **Legacy dataset formats** — v2.1→v3.0 conversion and depth-marker shims remain in the hot path.
5. **Extras / optional imports** — correct for install size, but easy to confuse when a CLI fails because an extra was omitted.
6. **Docstring / typing debt** — ruff `D` ignores and mypy exclusions cover large swaths of `src/lerobot`.

## Refactor strategies (preserve behavior)

| Strategy | Target | Safe first step |
| --- | --- | --- |
| Registry-only factories | `robots/utils.py`, teleop factory | Route remaining `elif` branches through `make_device_from_device_class`; keep aliases as registry entries |
| Split god modules | `processor/pipeline.py`, large `modeling_*.py` | Extract pure helpers + keep public class imports stable |
| Dataset facade | `LeRobotDataset` constructor kwargs | Group encoding/video/cache options into small config dataclasses |
| Sim-first wrappers | *this repo* `learning/` | Single smoke path for env + Hub dataset probe (done) |

## What this repo owns

| Path | Purpose |
| --- | --- |
| `scripts/lib/lerobot_env.sh` | Shared setup helpers (clone, venv, torch backend, extras) |
| `scripts/setup_lerobot.sh` | Thin orchestration entrypoint |
| `learning/` | Typed sim-first smoke helpers (`python -m learning.smoke`) |
| `.cursorrules` | Forces agents to read AGENT_GUIDE before hardware advice |
