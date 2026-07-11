"""Focused fail-closed contracts for the repository CI workflow."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _load_l4_collector():
    spec = importlib.util.spec_from_file_location(
        "collect_l4_stats_under_test", REPO_ROOT / "scripts" / "collect_l4_stats.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ci_checks_committed_rendered_artifacts_without_prerendering():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "render_meta.py --check" in workflow
    assert "render_meta.py --render convention-grade" not in workflow


def test_ci_test_and_l4_collection_fail_closed():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert '|| echo "no tests collected' not in workflow
    assert '|| echo "L4_STATS=0/0"' not in workflow
    assert "run: pytest -q" in workflow


def test_ci_pins_and_enforces_the_same_ruff_formatter_as_precommit():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    assert "pip install ruff==0.6.0 pyyaml" in workflow
    assert "ruff format --check . --config src/coding/ruff.toml" in workflow
    assert "rev: v0.6.0" in pre_commit
    assert "id: ruff-format\n        args: ['--config=src/coding/ruff.toml']" in pre_commit


def test_ci_build_installs_pytest_before_collecting_l4_stats():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    build = workflow.split("  build:", maxsplit=1)[1]

    install_index = build.index("pip install")
    collect_index = build.index("python scripts/collect_l4_stats.py")
    assert "pytest" in build[install_index:collect_index]
    assert "ruff==0.6.0" in build[install_index:collect_index]


def test_l4_collector_propagates_pytest_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    collector = _load_l4_collector()
    failed = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="68 passed, 1 failed in 1.00s\n", stderr=""
    )
    monkeypatch.setattr(collector.subprocess, "run", lambda *args, **kwargs: failed)

    assert collector.main() == 1
    captured = capsys.readouterr()
    assert "L4_STATS=" not in captured.out


def test_l4_collector_emits_deterministic_stats_after_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    collector = _load_l4_collector()
    passed = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="69 passed, 2 skipped in 1.00s\n", stderr=""
    )
    monkeypatch.setattr(collector.subprocess, "run", lambda *args, **kwargs: passed)

    assert collector.main() == 0
    assert capsys.readouterr().out == "L4_STATS=69/71"
