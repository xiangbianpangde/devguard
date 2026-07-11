"""Convergence report gates cannot be bypassed with an unversioned filename."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_report.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_report", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_report_name_requires_explicit_numeric_version():
    module = _load()

    assert module.REPORT_NAME.fullmatch("收束报告-v2.1.md")
    assert not module.REPORT_NAME.fullmatch("收束报告-current.md")
    assert not module.REPORT_NAME.fullmatch("收束报告-v2.md")
