"""Dashboard progress must come from the numbered STATUS truth table."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RENDERER = REPO_ROOT / "docs" / "templates" / "devguard" / "html-report-template" / "render.py"


def _load():
    spec = importlib.util.spec_from_file_location("dashboard_renderer", RENDERER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def test_real_status_uses_all_numbered_features():
    module = _load()
    status_path = REPO_ROOT / "STATUS.md"
    marker = re.search(
        r"devguard-progress:\s*completed=(\d+)\s+total=(\d+)",
        status_path.read_text(encoding="utf-8"),
    )
    assert marker

    rows = module.parse_status(status_path)
    done, total, _percent = module.compute_progress(rows)

    assert (done, total) == tuple(int(value) for value in marker.groups())


def test_checkmark_counts_as_completed(tmp_path):
    module = _load()
    status = tmp_path / "STATUS.md"
    status.write_text(
        "## 详细功能点列表\n\n"
        "| # | 功能点 | BDD | 状态 | 完成日期 |\n"
        "|---|---|---|---|---|\n"
        "| 1 | first | spec | ✅ 已完成 | 2026-07-11 |\n"
        "| 2 | second | spec | 🔄 进行中 | — |\n",
        encoding="utf-8",
    )

    assert module.compute_progress(module.parse_status(status)) == (1, 2, 50)
