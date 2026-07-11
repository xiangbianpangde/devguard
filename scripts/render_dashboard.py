#!/usr/bin/env python3
"""Render ``dashboard.html`` on Windows or POSIX without Bash or sed.

L4 values come from an actual pytest run. A failed test run or an
unparseable summary aborts before rendering, so a false ``0/0`` result can
never replace the previous artifact.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence


class DashboardError(RuntimeError):
    """Raised when test evidence or rendering is incomplete."""


COUNT_PATTERN = re.compile(
    r"(?P<count>\d+)\s+"
    r"(?P<kind>passed|failed|skipped|error|errors|xfailed|xpassed|deselected)\b"
)
TOTAL_KINDS = {"passed", "failed", "skipped", "error", "errors", "xfailed", "xpassed"}


def parse_pytest_counts(output: str) -> tuple[int, int]:
    """Parse passed/total from pytest's terminal summary."""
    counts: dict[str, int] = {}
    for match in COUNT_PATTERN.finditer(output):
        kind = match.group("kind")
        counts[kind] = counts.get(kind, 0) + int(match.group("count"))
    passed = counts.get("passed", 0)
    total = sum(count for kind, count in counts.items() if kind in TOTAL_KINDS)
    if total == 0:
        raise DashboardError("无法从 pytest 输出解析测试总数")
    return passed, total


def run_l4_tests(root: Path) -> tuple[int, int]:
    """Run the real convention suite and return its observable counts."""
    tests = root / "tests" / "conventions"
    if not tests.is_dir():
        raise DashboardError(f"L4 测试目录不存在：{tests}")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests), "-q"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = result.stdout + result.stderr
    passed, total = parse_pytest_counts(output)
    if result.returncode != 0:
        raise DashboardError(f"L4 测试失败（{passed}/{total} passed, exit={result.returncode}）")
    return passed, total


def render_dashboard(root: Path) -> tuple[int, int]:
    """Run L4 and render the dashboard only when the evidence is green."""
    root = root.resolve()
    passed, total = run_l4_tests(root)
    renderer = root / "docs" / "templates" / "devguard" / "html-report-template" / "render.py"
    meta = root / "conventions" / "_meta.yaml"
    status = root / "STATUS.md"
    output = root / "dashboard.html"
    missing = [path for path in (renderer, meta, status) if not path.is_file()]
    if missing:
        raise DashboardError(f"dashboard 输入缺失：{missing}")

    result = subprocess.run(
        [
            sys.executable,
            str(renderer),
            "--meta",
            str(meta),
            "--status",
            str(status),
            "--out",
            str(output),
            "--l4-passed",
            str(passed),
            "--l4-total",
            str(total),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise DashboardError(f"dashboard 渲染失败：{detail or '无诊断输出'}")
    return passed, total


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="跨平台渲染 dashboard.html")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="项目根目录（默认脚本上一级）",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        passed, total = render_dashboard(args.root)
    except DashboardError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"L4_STATS={passed}/{total}")
    print(f"OK: {args.root.resolve() / 'dashboard.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
