"""CLI smoke tests (no Hub download)."""

from __future__ import annotations

from learning.smoke import build_parser, main


def test_build_parser_defaults() -> None:
    args = build_parser().parse_args([])
    assert args.dataset == "lerobot/pusht"
    assert args.episodes == [0]
    assert args.skip_dataset is False


def test_main_skip_dataset_json(capsys) -> None:
    code = main(["--skip-dataset", "--json"])
    captured = capsys.readouterr()
    assert code in (0, 1)  # 1 if lerobot not importable outside the venv
    assert '"recommended_policy_device"' in captured.out
    assert "dataset" not in captured.out or '"dataset"' not in captured.out
