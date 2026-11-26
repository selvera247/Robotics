"""Unit tests for dataset probing with a stub LeRobotDataset."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

from learning.dataset_probe import DatasetProbeResult, probe_dataset


class _FakeDataset:
    def __init__(self, repo_id: str, **kwargs: Any) -> None:
        self.repo_id = repo_id
        self.num_episodes = 1
        self.features = {
            "observation.state": {"dtype": "float32"},
            "action": {"dtype": "float32"},
        }

    def __len__(self) -> int:
        return 3

    def __getitem__(self, index: int) -> dict[str, Any]:
        return {
            "observation.state": [0.0],
            "action": [0.0],
            "index": index,
        }


def test_probe_dataset_with_stub(monkeypatch) -> None:
    stub = ModuleType("lerobot.datasets.lerobot_dataset")
    stub.LeRobotDataset = _FakeDataset  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "lerobot.datasets.lerobot_dataset", stub)

    result = probe_dataset("lerobot/pusht", episodes=[0])

    assert isinstance(result, DatasetProbeResult)
    assert result.repo_id == "lerobot/pusht"
    assert result.num_episodes == 1
    assert result.num_frames == 3
    assert "action" in result.feature_names
    assert "observation.state" in result.sample_keys
    assert result.to_dict()["num_frames"] == 3
