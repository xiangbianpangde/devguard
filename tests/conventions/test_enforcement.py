"""The enforcement metric is measured with actual staged fault injections."""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_enforcement.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_enforcement", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_fault_injection_matrix_blocks_at_least_90_percent():
    mod = _load()
    report = mod.run_matrix(REPO_ROOT)
    assert report.total >= 10
    assert report.blocked / report.total * 100 >= 90
    assert all(case.mutation and case.expected_message for case in report.cases)


def test_report_exposes_blocked_over_total():
    mod = _load()
    report = mod.run_matrix(REPO_ROOT)
    output = mod.format_report(report, threshold=90)
    assert f"{report.blocked}/{report.total}" in output
    assert "强制性拦截率" in output
