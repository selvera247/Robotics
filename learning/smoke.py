"""CLI smoke path for simulation-first learning (no robot hardware).

Usage (venv activated, from repo root)::

    python -m learning.smoke
    python -m learning.smoke --dataset lerobot/pusht --episodes 0
"""

from __future__ import annotations

import argparse
import json
import sys

from learning.dataset_probe import probe_dataset
from learning.env_report import collect_env_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the LeRobot learning env and optionally probe a Hub dataset.",
    )
    parser.add_argument(
        "--dataset",
        default="lerobot/pusht",
        help="Hub dataset repo id to probe (default: lerobot/pusht).",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        nargs="*",
        default=[0],
        help="Episode indices to load (default: 0). Pass nothing after the flag for all.",
    )
    parser.add_argument(
        "--skip-dataset",
        action="store_true",
        help="Only print the environment report.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    env = collect_env_report()

    payload: dict = {"env": env.to_dict(), "recommended_policy_device": env.recommended_policy_device}

    if not args.skip_dataset:
        episodes = args.episodes if args.episodes is not None else None
        # argparse with nargs='*' and default=[0]: empty `--episodes` → []
        if episodes == []:
            episodes = None
        probe = probe_dataset(args.dataset, episodes=episodes)
        payload["dataset"] = probe.to_dict()

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Environment")
        print(f"  python:     {env.python_version}")
        print(f"  lerobot:    {env.lerobot_version}")
        print(f"  torch:      {env.torch_version}")
        print(f"  cuda:       {env.cuda_available}")
        print(f"  ffmpeg:     {env.ffmpeg_version or 'missing'}")
        print(f"  device hint:{env.recommended_policy_device}")
        if "dataset" in payload:
            ds = payload["dataset"]
            print("Dataset probe")
            print(f"  repo_id:    {ds['repo_id']}")
            print(f"  episodes:   {ds['num_episodes']}")
            print(f"  frames:     {ds['num_frames']}")
            print(f"  features:   {', '.join(ds['feature_names'][:8])}...")

    if env.lerobot_version is None:
        print("LeRobot is not importable. Activate lerobot/.venv and re-run.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
