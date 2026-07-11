"""Consistency scoring must use executable and cross-file facts."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_consistency.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_consistency", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _write(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_empty_evidence_files_cannot_manufacture_a_high_score(tmp_path):
    mod = _load()
    # The old implementation awarded 90% for Path.exists(). Empty evidence must
    # now fail semantic and executable checks.
    for rel in ("README.md", "commitlint.config.js", ".spectral.yaml"):
        _write(tmp_path, rel)

    report = mod.evaluate_repository(
        tmp_path, command_runner=lambda _command: (1, "injected failure")
    )

    assert report.score < 80
    assert report.total > 0
    assert any(d.passed < d.total for d in report.dimensions)


def test_progress_projection_mismatch_is_reported(tmp_path):
    mod = _load()
    _write(
        tmp_path,
        "STATUS.md",
        "<!-- devguard-progress: completed=49 total=49 -->\n",
    )
    _write(
        tmp_path,
        "docs/plan/开发清单.md",
        "<!-- devguard-progress: completed=48 total=49 -->\n",
    )
    _write(
        tmp_path,
        "CLAUDE.md",
        "<!-- devguard-progress: completed=49 total=49 -->\n",
    )

    dimension = mod.evaluate_progress_truth(tmp_path)

    assert dimension.passed == 2
    assert dimension.total == 5
    assert any("开发清单" in fact.detail for fact in dimension.facts if not fact.passed)


def test_ci_template_and_formatter_drift_are_scored(tmp_path):
    mod = _load()
    _write(tmp_path, ".github/workflows/ci.yml", "pip install ruff\n")
    _write(
        tmp_path,
        "docs/templates/devguard/.github/workflows/ci.yml",
        "different\n",
    )
    _write(tmp_path, ".pre-commit-config.yaml", "rev: v0.6.0\n")

    dimension = mod.evaluate_ci_projection(tmp_path)

    assert dimension.total == 2
    assert dimension.passed == 0


def test_default_runner_forces_utf8_for_windows_subprocesses(
    monkeypatch: pytest.MonkeyPatch,
):
    mod = _load()
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, "通过\n", "")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    assert mod._default_runner(["python", "gate.py"]) == (0, "通过")
    environment = captured["env"]
    assert isinstance(environment, dict)
    assert environment["PYTHONUTF8"] == "1"
    assert environment["PYTHONIOENCODING"] == "utf-8"


def test_format_report_exposes_each_dimension_fraction(tmp_path):
    mod = _load()
    report = mod.evaluate_repository(
        tmp_path, command_runner=lambda _command: (1, "not configured")
    )

    output = mod.format_report(report, threshold=80)

    for dimension in report.dimensions:
        assert f"{dimension.passed}/{dimension.total}" in output
    assert "总计:" in output
