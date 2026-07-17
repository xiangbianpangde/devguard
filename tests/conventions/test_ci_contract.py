"""Focused fail-closed contracts for the repository CI workflow."""

from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _expected_ruff_version() -> str:
    """ruff 版本的单一真源：conventions/_meta.yaml 的 toolchain 节"""
    meta = yaml.safe_load((REPO_ROOT / "conventions" / "_meta.yaml").read_text(encoding="utf-8"))
    version = meta["toolchain"]["ruff"]
    assert isinstance(version, str) and version, "toolchain.ruff 必须是非空字符串"
    return version


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
    version = _expected_ruff_version()

    assert f"pip install ruff=={version} pyyaml" in workflow
    assert "ruff format --check . --config src/coding/ruff.toml" in workflow
    assert f"rev: v{version}" in pre_commit
    assert "id: ruff-format\n        args: ['--config=src/coding/ruff.toml']" in pre_commit


def test_toolchain_ruff_version_is_single_source_for_all_dependency_files():
    """_meta.yaml toolchain.ruff 必须与 requirements-dev / pyproject / 全 CI 钉版一致"""
    version = _expected_ruff_version()
    requirements = (REPO_ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert f"ruff=={version}" in requirements, "requirements-dev.txt 与 toolchain 真源不一致"
    assert f'"ruff=={version}"' in pyproject, "pyproject.toml dev extras 与 toolchain 真源不一致"
    pins = set(re.findall(r"ruff==([0-9][0-9a-z.]*)", workflow))
    assert pins == {version}, f"CI 中 ruff 钉版不统一：{pins}，期望 {{{version}}}"


def test_ci_build_installs_pytest_before_collecting_l4_stats():
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    build = workflow.split("  build:", maxsplit=1)[1]

    install_index = build.index("pip install")
    collect_index = build.index("python scripts/collect_l4_stats.py")
    assert "pytest" in build[install_index:collect_index]
    assert f"ruff=={_expected_ruff_version()}" in build[install_index:collect_index]


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
