"""Crossing a planned convergence node must be blocked until closeout."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_convergence_gate.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_convergence_gate", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_marker_is_required_fail_closed():
    mod = _load()
    errors = mod.evaluate_gate("no marker", "| 1 | x | ✅ |", "| 1 | x | ✅ |")
    assert errors and "标记" in " ".join(errors)


def test_crossing_pending_node_is_blocked():
    mod = _load()
    marker = "<!-- convergence-gate: nodes=46,49 last_converged_fp=46 -->"
    head = "| 49 | x | ⏳ |\n| 50 | y | ⏳ |"
    staged = "| 49 | x | ✅ |\n| 50 | y | ✅ |"
    errors = mod.evaluate_gate(marker, head, staged)
    assert errors and "#49" in " ".join(errors)


def test_delivering_node_itself_is_allowed():
    mod = _load()
    marker = "<!-- convergence-gate: nodes=49 last_converged_fp=46 -->"
    head = "| 49 | x | ⏳ |"
    staged = "| 49 | x | ✅ |"
    assert not mod.evaluate_gate(marker, head, staged)
