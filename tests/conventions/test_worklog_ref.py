"""Worklog references must resolve to a real staged blob."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_worklog_ref.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_worklog_ref", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-qm", "seed")
    return tmp_path


def test_phantom_reference_is_blocked(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    errors = mod.validate_worklog_reference("feat: x worklogs/2026-07-10_x.md", root)
    assert errors
    assert "暂存" in " ".join(errors)


def test_staged_worklog_reference_passes(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    worklog = root / "worklogs" / "2026-07-10_x.md"
    worklog.parent.mkdir()
    worklog.write_text("# x\n", encoding="utf-8")
    _git(root, "add", "worklogs/2026-07-10_x.md")
    assert not mod.validate_worklog_reference("feat: x worklogs/2026-07-10_x.md", root)


def test_unaudited_skip_marker_is_blocked(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    errors = mod.validate_worklog_reference("hotfix [skip-worklog]", root)
    assert errors
    assert "豁免" in " ".join(errors) or "登记" in " ".join(errors)
