"""L4 perf baseline (V2.5).

Measures current L4 suite runtime. Warns if future run > baseline * 1.5.
Does NOT fail on slow (avoid flaky CI blocking commits); only warn + log.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Baseline (V2.5 first measurement): 53 tests in 2.69s
# 注：V2.5 首测口径为当时 53 个 L4 测试；当前套件 200+，本基线仅作数量级参考，
# 超阈值只 WARN 不 FAIL（见 main()），避免性能噪音阻塞提交。
BASELINE_SECONDS = 2.69
TOLERANCE = 1.5


def test_perf_baseline_script_loadable() -> None:
    """基线脚本可被 pytest 收集加载，且基线常量取值合理（V2.5 起仅 warn 不 fail）。"""
    assert BASELINE_SECONDS > 0, "BASELINE_SECONDS 必须为正"
    assert TOLERANCE >= 1.0, "TOLERANCE 必须 >= 1.0"


def main() -> int:
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/conventions/", "-q", "--tb=line"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start
    threshold = BASELINE_SECONDS * TOLERANCE

    msg = f"L4 elapsed {elapsed:.2f}s baseline {BASELINE_SECONDS}s tol {TOLERANCE}"
    thr = f"thr {threshold:.2f}s"
    print(msg, thr)  # noqa: T201
    if result.returncode != 0:
        print("FAIL: L4 tests had failures")  # noqa: T201
        print(result.stdout[-2000:])  # noqa: T201
        print(result.stderr[-1000:])  # noqa: T201
        return 1
    if elapsed > threshold:
        print(f"WARN {elapsed:.2f}s > {threshold:.2f}s perf regression")  # noqa: T201
    else:
        print(f"OK {elapsed:.2f}s within {threshold:.2f}s")  # noqa: T201
    return 0


if __name__ == "__main__":
    sys.exit(main())
