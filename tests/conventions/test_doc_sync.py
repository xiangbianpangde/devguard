"""Feature-point structure must stay synchronized across truth projections."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_doc_sync.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_doc_sync", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_status_only_feature_addition_is_rejected():
    mod = _load()
    errors, structural = mod.sync_errors(
        {48}, {48, 49}, {48}, {48}, ai_context_staged=True
    )
    assert structural
    assert errors


def test_synchronized_addition_requires_ai_context_projection():
    mod = _load()
    errors, _ = mod.sync_errors({48}, {48, 49}, {48}, {48, 49}, ai_context_staged=False)
    assert any("AI" in error or "CLAUDE" in error for error in errors)


def test_extractors_accept_numbered_rows():
    mod = _load()
    assert mod.status_fps("| #49 x | ✅ |\n| 48 | y | ✅ |") == {48, 49}
    assert mod.plan_fps("| 49 | x | ✅ |") == {49}
