"""New files must follow the FILE_GRAPH placement contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_file_placement.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_file_placement", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_root_stray_and_unknown_docs_section_are_blocked():
    mod = _load()
    assert mod.placement_error("scratch.md")
    assert mod.placement_error("docs/random/note.md")


def test_known_areas_pass():
    mod = _load()
    for path in (
        "README.md",
        "scripts/check_x.py",
        "tests/conventions/test_x.py",
        "docs/specs/x.md",
        ".github/workflows/ci.yml",
    ):
        assert mod.placement_error(path) is None
