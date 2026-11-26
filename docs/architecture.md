# LeRobot architecture (learning notes)

Companion to upstream [`AGENTS.md`](https://github.com/huggingface/lerobot/blob/main/AGENTS.md) and [`AGENT_GUIDE.md`](https://github.com/huggingface/lerobot/blob/main/AGENT_GUIDE.md). This repo clones LeRobot under `./lerobot` (gitignored); treat that tree as the system under study.

## Mental model

LeRobot is four contracts glued by configs (draccus `ChoiceRegistry`) and processors:

| Layer | Role | Key types / paths |
| --- | --- | --- |
| **Datasets** | Episode-aware Hub/disk storage + video decode | `LeRobotDataset` → `src/lerobot/datasets/` |
| **Policies** | Trainable `nn.Module`s with Hub push/pull | `PreTrainedPolicy` → `src/lerobot/policies/` |
| **Robots / teleops** | Real hardware I/O | `Robot`, `Teleoperator` → `robots/`, `teleoperators/`, `motors/`, `cameras/` |
| **Envs / sim** | Gymnasium benchmarks + sim-as-robot | `EnvConfig`, `SimRobot` → `envs/`, `sim/` |

Also important: `rollout/` (real-robot deploy), `cameras/` / `motors/`, `env_server/` + `remote_inference/` for served sim/policy.

**Stable shared language:** the LeRobot **feature dict** (parquet column schema + `PolicyFeature`). Robots emit raw dicts; processors + `feature_utils` convert; policies consume tensors shaped by it. Changing joint order, camera names, or fps without updating meta/processors/policy features breaks train→deploy.

## End-to-end data flows

```
Record:  teleop/policy → robot.get_observation/send_action → LeRobotDataset.create/writer → Hub
Train:   Hub dataset → DataLoader (+ processors) → policy.forward → checkpoint (+ optional Hub push)
Eval:    Hub/local policy → make_env(env.type) → lerobot-eval rollouts → success metrics
Rollout: Hub/local policy → real Robot (or SimRobot) → lerobot-rollout
```

CLI entrypoints live in `lerobot/pyproject.toml` `[project.scripts]` → `src/lerobot/scripts/`. Nested overrides use draccus (`--policy.type=act --dataset.repo_id=…`); `--policy.path=` loads a Hub/local config then applies further `--policy.*` flags.

## SO-101 / LeKiwi specifics

- SO-100/101 share `SOFollower` / `SOLeader` with `@register_subclass("so100_*" | "so101_*")` aliases — **same classes** in code (`robots/so_follower`, `teleoperators/so_leader`).
- LeKiwi adds ZMQ host/client (`robots/lekiwi`) on Feetech motors (`extra: feetech`, `lekiwi`).
- `lerobot-record` still special-cases `robot.name == "lekiwi_client"` for multi-teleop; treat that as a capability gap, not a second API.
- Simulation-first: Hub datasets (`lerobot/pusht`, …) + `lerobot-eval --env.type=pusht` before USB/calibrate.

## Problem areas (upstream — do not fork lightly)

Prioritized from an architecture map + code-smell pass over `src/lerobot`:

| Sev | Theme | Evidence |
| --- | --- | --- |
| High | Serial-arm / bi-arm **copy-paste** | `so_follower` / `koch_follower` / `omx_follower` (+ leaders); bi wrappers re-list config fields |
| High | **Factory + record_loop** name coupling | `robots/utils.py` / `teleoperators/utils.py` elif trees; `lerobot_record.py` checks `lekiwi_client` / leader class set |
| High | **Video I/O** cost | `video_utils.py`, per-sample decode; ThreadPool churn on multi-cam; parquet vs lance dual path |
| High | **Stringly feature APIs** | `RobotAction` / `RobotObservation` as `dict[str, Any]`; `"{motor}.pos"`; `use_degrees` dual norms |
| Med | God modules | Optional VLA `modeling_*.py` 2k–4.7k LOC; `processor/pipeline.py`, `motors_bus.py`, train/eval scripts |
| Med | Config / alias sprawl | `so100_*`≡`so101_*`; dual LeKiwi host config names; naming folklore in `make_device_from_device_class` |
| Med | **Hardware test gaps** | Few robot/teleop tests; no dedicated so101 test; thin LeKiwi host/client + multi-teleop coverage |
| Low | Legacy / transitional | v2.1→v3.0 converter; `video_reader`→pyav; deprecated transforms; env-var renames |

Learner-relevant cores (ACT/Diffusion, SO follower) are comparatively small; most LOC is optional VLA/vendor + dataset I/O.

## Refactor strategies (preserve behavior)

Suggested upstream order:

1. **SerialArmFollower / SerialArmLeader** (+ one bimanual composer) — biggest win for SO-101 contributors  
2. **Capability-based factories / record_loop** (`supports_multi_teleop`, …) instead of `robot.name == …`  
3. **Feature schema validation** at connect/dataset-create; keep string wire format for parquet  
4. **Persistent decoder pools** + episode-subset defaults for teaching paths  
5. **Parameterized hardware contract tests** over mocked `SerialMotorsBus`  
6. Split god modules; deprecate dual formats/aliases with warnings  

| This repo (done) | Purpose |
| --- | --- |
| `scripts/lib/lerobot_env.sh` + `setup_lerobot.sh` | Modular setup; single extras source of truth |
| `learning/` | Typed sim-first smoke (`python -m learning.smoke`) |
| `.cursorrules` / this doc | Point agents at AGENT_GUIDE; do not vendor `./lerobot` |
