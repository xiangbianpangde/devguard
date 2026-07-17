"""Exemptions require a catalog entry and a newly staged usage row."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_exemption_log.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_exemption_log", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _registry(usage: str = "") -> str:
    return (
        "## 二、已登记豁免标记\n\n"
        "| 豁免标记 | 钩子 | 说明 |\n|---|---|---|\n"
        "| `[skip-worklog]` | check_worklog_ref.py | emergency |\n\n"
        "## 三、豁免使用记录\n\n"
        "| 日期 | 范围 | 钩子 | 豁免标记 | 申请人 | 为何 |\n|---|---|---|---|---|---|\n" + usage
    )


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    path = tmp_path / "meta" / "豁免清单.md"
    path.parent.mkdir()
    path.write_text(_registry(), encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-qm", "seed")
    return tmp_path


def test_catalog_only_is_not_an_auditable_exemption(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    errors = mod.validate_exemptions("fix [skip-worklog]", root)
    assert errors
    assert "使用记录" in " ".join(errors)


def test_new_usage_row_allows_registered_marker(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    path = root / "meta" / "豁免清单.md"
    path.write_text(
        _registry(
            "| 2026-07-10 | hotfix | check_worklog_ref.py | `[skip-worklog]` | owner | outage |\n"
        ),
        encoding="utf-8",
    )
    _git(root, "add", "meta/豁免清单.md")
    assert not mod.validate_exemptions("fix [skip-worklog]", root)


def test_unregistered_marker_is_blocked(tmp_path):
    mod = _load()
    root = _repo(tmp_path)
    assert mod.validate_exemptions("fix [skip-invented]", root)
