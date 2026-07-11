"""Cross-platform dashboard entry tests (no Bash or hard-coded L4 counts)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRY_PATH = REPO_ROOT / "scripts" / "render_dashboard.py"


def load_entry():
    spec = importlib.util.spec_from_file_location("render_dashboard", ENTRY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        ("69 passed in 1.23s", (69, 69)),
        ("2 failed, 7 passed, 1 skipped in 0.30s", (7, 10)),
        ("3 passed, 2 xfailed, 1 xpassed in 0.10s", (3, 6)),
    ],
)
def test_parse_pytest_counts_is_dynamic(summary, expected):
    module = load_entry()
    assert module.parse_pytest_counts(summary) == expected


def test_parse_pytest_counts_rejects_missing_summary():
    module = load_entry()
    with pytest.raises(module.DashboardError, match="pytest"):
        module.parse_pytest_counts("collection crashed")


def test_windows_friendly_entry_runs_tests_then_renders_in_temp_project(tmp_path):
    tests_dir = tmp_path / "tests" / "conventions"
    renderer_dir = tmp_path / "docs" / "templates" / "devguard" / "html-report-template"
    tests_dir.mkdir(parents=True)
    renderer_dir.mkdir(parents=True)
    (tests_dir / "test_sample.py").write_text(
        "def test_one():\n    assert True\n\ndef test_two():\n    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )
    (tmp_path / "conventions").mkdir()
    (tmp_path / "conventions" / "_meta.yaml").write_text(
        "project: Temp\n", encoding="utf-8"
    )
    (tmp_path / "STATUS.md").write_text("# Status\n", encoding="utf-8")
    (renderer_dir / "render.py").write_text(
        """import argparse
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--meta'); p.add_argument('--status'); p.add_argument('--out')
p.add_argument('--l4-passed'); p.add_argument('--l4-total')
a = p.parse_args()
Path(a.out).write_text(f'{a.l4_passed}/{a.l4_total}', encoding='utf-8')
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(ENTRY_PATH), "--root", str(tmp_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "dashboard.html").read_text(encoding="utf-8") == "2/2"
    assert "L4_STATS=2/2" in result.stdout


def test_package_dashboard_script_has_no_bash_or_hard_coded_counts():
    package_json = (REPO_ROOT / "package.json").read_text(encoding="utf-8")
    assert '"dashboard": "python scripts/render_dashboard.py"' in package_json
    assert "render_dashboard.sh" not in package_json
    assert "--l4-passed" not in package_json
