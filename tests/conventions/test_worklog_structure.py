"""Worklogs must carry completion, verification and hand-off evidence."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_worklog_structure.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_worklog_structure", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_narrative_only_worklog_is_rejected():
    mod = _load()
    errors, _warnings = mod.check_content("worklogs/2026-07-10_x.md", "# notes\ntext")
    assert len(errors) >= 4


def test_template_shaped_worklog_passes():
    mod = _load()
    content = (
        "# log\n## 做了什么\n- [x] fixed\n"
        "## 验证结果\n- command: exit 0\n## 下一步\n- handoff\n"
    )
    errors, _warnings = mod.check_content("worklogs/2026-07-10_x.md", content)
    assert not errors
