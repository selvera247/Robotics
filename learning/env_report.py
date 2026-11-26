"""Environment introspection used by setup verification and learning smoke checks."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class EnvReport:
    """Snapshot of the local LeRobot runtime (CPU/GPU, ffmpeg, package versions)."""

    python_version: str
    lerobot_version: str | None
    torch_version: str | None
    cuda_available: bool
    ffmpeg_path: str | None
    ffmpeg_version: str | None
    has_nvidia_smi: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def recommended_policy_device(self) -> str:
        return "cuda" if self.cuda_available else "cpu"


def _ffmpeg_version() -> str | None:
    path = shutil.which("ffmpeg")
    if not path:
        return None
    try:
        out = subprocess.check_output([path, "-version"], text=True, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        return None
    first = out.splitlines()[0] if out else ""
    return first.strip() or None


def collect_env_report() -> EnvReport:
    """Collect versions from the active interpreter (expects lerobot venv activated)."""
    import sys

    lerobot_version: str | None
    try:
        from lerobot.__version__ import __version__ as lr_ver

        lerobot_version = lr_ver
    except Exception:  # noqa: BLE001 — report missing install cleanly
        lerobot_version = None

    torch_version: str | None
    cuda_available = False
    try:
        import torch

        torch_version = torch.__version__
        cuda_available = bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001
        torch_version = None

    return EnvReport(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        lerobot_version=lerobot_version,
        torch_version=torch_version,
        cuda_available=cuda_available,
        ffmpeg_path=shutil.which("ffmpeg"),
        ffmpeg_version=_ffmpeg_version(),
        has_nvidia_smi=shutil.which("nvidia-smi") is not None,
    )
