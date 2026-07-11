"""Worklog and STATUS must be staged together with matching dates."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_status_updated.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_status_updated", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_worklog_without_status_is_rejected():
    mod = _load()
    errors = mod.validate_status_sync({"worklogs/2026-07-10_x.md"}, lambda _path: "")
    assert errors and "STATUS.md" in " ".join(errors)


def test_matching_status_date_passes():
    mod = _load()
    files = {"worklogs/2026-07-10_x.md", "STATUS.md"}
    assert not mod.validate_status_sync(files, lambda _path: "> 更新: 2026-07-10\n")
