"""Run the L4 convention suite and emit its passed/total counts.

The command fails closed: a failing or unparseable pytest run never emits a
successful ``L4_STATS`` record. Output on success: ``L4_STATS=64/64``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NON_PASSING_SUCCESS_OUTCOMES = ("skipped", "xfailed", "xpassed")


def _count_outcome(output: str, outcome: str) -> int:
    """Extract one pytest summary outcome count, defaulting to zero."""
    match = re.search(rf"(\d+)\s+{outcome}\b", output)
    return int(match.group(1)) if match else 0


def main() -> int:
    # pytest 是固定 binary，args 来自 tests/ 目录（仓库内）受信任
    result = subprocess.run(  # noqa: S603, S607
        [sys.executable, "-m", "pytest", "tests/conventions/", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(output, file=sys.stderr, end="")
        return 1

    # 匹配 "= 64 passed in 2.99s" 或 "64 passed in 2.99s"
    passed_match = re.search(r"(\d+)\s+passed", output)

    if not passed_match:
        print("FAIL: 无法从 pytest 输出解析 L4 通过数", file=sys.stderr)
        print(output, file=sys.stderr, end="")
        return 1

    passed = int(passed_match.group(1))
    non_passing = sum(_count_outcome(output, outcome) for outcome in NON_PASSING_SUCCESS_OUTCOMES)
    total = passed + non_passing
    print(f"L4_STATS={passed}/{total}", end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
