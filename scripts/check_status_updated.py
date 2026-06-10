#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_status_updated.py — commit-msg 钩子：worklog ↔ STATUS.md 同步拦截
============================================================
依据：ai-workflow 07-汇报「每功能点完成 → 更新 worklog + STATUS（必做）」
      + 流程强制化方案 #37（汇报流程强制化 Phase 1）

判定逻辑：
  1. commit message 含 [skip-status] → 直接放行
  2. 本次提交未改任何 worklogs/<date>_*.md → 与本钩子无关，放行
  3. 改了 worklog，但 STATUS.md 不在本次 staged 变更中 → FAIL
  4. 改了 worklog 且 STATUS.md 也 staged，但 STATUS「> 更新:」日期
     与本次 staged 的最新 worklog 日期不一致 → FAIL（口径漂移）
  5. 全部满足 → PASS

为什么是 commit-msg 阶段而非 pre-commit 阶段：
  豁免标记 [skip-status] 写在 commit message 里，pre-commit 阶段读不到
  commit message；commit-msg 阶段既能读 message 又能 `git diff --cached`。

用法（pre-commit 框架调用）:
    python scripts/check_status_updated.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = "STATUS.md"
SKIP_MARKER = "[skip-status]"

# 顶层日志：worklogs/YYYY-MM-DD_*.md（不含 worklogs/decisions/ 下的 ADR）
WORKLOG_RE = re.compile(r"^worklogs/(\d{4}-\d{2}-\d{2})[_\-\.].+\.md$", re.IGNORECASE)
STATUS_DATE_RE = re.compile(r"更新[:：]\s*(\d{4}-\d{2}-\d{2})")


def staged_files() -> list[str]:
    """`git diff --cached --name-only` 的 staged 路径列表（正斜杠归一）"""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [
        line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()
    ]


def status_update_date(staged: list[str]) -> str | None:
    """读 STATUS.md 的「> 更新: YYYY-MM-DD」日期。

    优先读 staged 版本（`git show :STATUS.md`），读不到再退回工作区文件。
    """
    content = ""
    try:
        content = subprocess.run(
            ["git", "show", f":{STATUS_FILE}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        path = REPO_ROOT / STATUS_FILE
        if path.exists():
            content = path.read_text(encoding="utf-8")
    m = STATUS_DATE_RE.search(content)
    return m.group(1) if m else None


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_status_updated.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-status]，跳过 STATUS 同步检查")
        return 0

    staged = staged_files()

    # 本次提交里的顶层 worklog 文件 + 其日期
    worklog_dates: list[str] = []
    for f in staged:
        m = WORKLOG_RE.match(f)
        if m:
            worklog_dates.append(m.group(1))

    if not worklog_dates:
        # 没动 worklog，本钩子不管
        return 0

    # 动了 worklog → STATUS.md 必须同 staged
    if STATUS_FILE not in staged:
        print("FAIL: 本次提交修改了 worklog，但 STATUS.md 未同步更新", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  ai-workflow 07-汇报：每功能点完成 → 更新 worklog + STATUS（必做）",
            file=sys.stderr,
        )
        print("  修复: 更新 STATUS.md 并 `git add STATUS.md`", file=sys.stderr)
        print("  豁免: commit message 末尾加 [skip-status]", file=sys.stderr)
        return 1

    # STATUS「> 更新:」日期需与本次最新 worklog 日期一致
    latest_worklog_date = max(worklog_dates)
    sdate = status_update_date(staged)
    if sdate is None:
        print(
            "FAIL: STATUS.md 缺「> 更新: YYYY-MM-DD」行，无法核对口径", file=sys.stderr
        )
        print(
            "  修复: 在 STATUS.md 顶部加 `> 更新: YYYY-MM-DD（...）`", file=sys.stderr
        )
        print("  豁免: commit message 末尾加 [skip-status]", file=sys.stderr)
        return 1
    if sdate != latest_worklog_date:
        print(
            f"FAIL: STATUS.md 更新日期({sdate})"
            f"与最新 worklog({latest_worklog_date})不一致，[skip-status] 豁免",
            file=sys.stderr,
        )
        print(
            "  修复: 把 STATUS.md 顶部「> 更新:」日期改成与 worklog 一致",
            file=sys.stderr,
        )
        print("  豁免: commit message 末尾加 [skip-status]", file=sys.stderr)
        return 1

    print(f"OK: worklog({latest_worklog_date}) ↔ STATUS.md({sdate}) 同步")
    return 0


if __name__ == "__main__":
    sys.exit(main())
