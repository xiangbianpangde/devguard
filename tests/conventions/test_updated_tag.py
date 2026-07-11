"""Managed staged documents must refresh their update tag."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_updated_tag.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_updated_tag", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_missing_and_stale_tags_are_rejected():
    mod = _load()
    assert mod.validate_update_tags(["docs/specs/x.md"], lambda _path: "# x\n", "2026-07-10")
    assert mod.validate_update_tags(
        ["docs/specs/x.md"],
        lambda _path: "> 更新: 2026-07-09\n",
        "2026-07-10",
    )


def test_current_tag_and_excluded_template_pass():
    mod = _load()
    assert not mod.validate_update_tags(
        ["docs/specs/x.md"],
        lambda _path: "> 更新: 2026-07-10\n",
        "2026-07-10",
    )
    assert not mod.in_scope("docs/templates/x.md")
