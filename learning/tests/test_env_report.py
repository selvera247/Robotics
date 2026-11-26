"""Unit tests for environment reporting (no Hub network required)."""

from __future__ import annotations

from learning.env_report import EnvReport, collect_env_report


def test_collect_env_report_shape() -> None:
    report = collect_env_report()
    assert isinstance(report, EnvReport)
    assert report.python_version.count(".") == 2
    data = report.to_dict()
    assert "torch_version" in data
    assert "ffmpeg_path" in data


def test_recommended_policy_device_matches_cuda_flag() -> None:
    cpu = EnvReport(
        python_version="3.12.0",
        lerobot_version="0.7.1",
        torch_version="2.15.0+cpu",
        cuda_available=False,
        ffmpeg_path="/usr/bin/ffmpeg",
        ffmpeg_version="ffmpeg version 6",
        has_nvidia_smi=False,
    )
    gpu = EnvReport(
        python_version="3.12.0",
        lerobot_version="0.7.1",
        torch_version="2.15.0+cu128",
        cuda_available=True,
        ffmpeg_path="/usr/bin/ffmpeg",
        ffmpeg_version="ffmpeg version 6",
        has_nvidia_smi=True,
    )
    assert cpu.recommended_policy_device == "cpu"
    assert gpu.recommended_policy_device == "cuda"
