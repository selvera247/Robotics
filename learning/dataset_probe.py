"""Load a public LeRobotDataset and summarize it without training or hardware."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DatasetProbeResult:
    """Compact view of a Hub/local LeRobot dataset used for learning smoke checks."""

    repo_id: str
    num_episodes: int
    num_frames: int
    feature_names: tuple[str, ...]
    sample_keys: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def probe_dataset(
    repo_id: str,
    *,
    episodes: list[int] | None = None,
    download_videos: bool = True,
) -> DatasetProbeResult:
    """Download (if needed) and open ``repo_id``, returning episode/frame/feature stats.

    Args:
        repo_id: Hugging Face dataset id, e.g. ``lerobot/pusht``.
        episodes: Optional subset of episode indices to load (keeps downloads light).
        download_videos: Forwarded to ``LeRobotDataset``; keep True for real training data.

    Returns:
        Immutable summary suitable for printing or tests.
    """
    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    dataset = LeRobotDataset(
        repo_id,
        episodes=episodes,
        download_videos=download_videos,
    )
    sample = dataset[0]
    return DatasetProbeResult(
        repo_id=dataset.repo_id,
        num_episodes=int(dataset.num_episodes),
        num_frames=len(dataset),
        feature_names=tuple(dataset.features.keys()),
        sample_keys=tuple(sample.keys()),
    )
