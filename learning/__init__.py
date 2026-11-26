"""Thin learning helpers around Hugging Face LeRobot (sim-first, no hardware).

These wrappers do not reimplement LeRobot. They provide a small, typed surface for
common learning workflows so README one-liners and agent sessions share one path.
"""

from learning.dataset_probe import DatasetProbeResult, probe_dataset
from learning.env_report import EnvReport, collect_env_report

__all__ = [
    "DatasetProbeResult",
    "EnvReport",
    "collect_env_report",
    "probe_dataset",
]
