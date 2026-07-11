"""Executable ECC-to-DevGuard capability alignment contract."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_ecc_alignment.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_ecc_alignment", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ecc_alignment_has_ten_fact_backed_domains_and_meets_threshold():
    module = load_checker()

    report = module.evaluate(REPO_ROOT)

    assert report.total == 10
    assert report.passed == 10
    assert report.score == 100.0


def test_ecc_alignment_cli_passes_at_required_threshold():
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--threshold", "80"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "10/10" in result.stdout
