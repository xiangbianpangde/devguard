#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_convergence_gate.py — 收束闸门 L1 检查（07-ai-workflow 收束节点 强制化）
============================================================
把"预设收束节点 = 硬闸门"从纸面规范变成可执行检查。依据：
  - conventions/ai-workflow_AI协作开发流程/03-第一步_编写计划.md §1.0 / §1.6
  - conventions/ai-workflow_AI协作开发流程/06-第三步_收束节点.md §2.1 / §2.2

强制两件事：
  1. docs/plan/开发清单.md 头部必须声明：
       - `> 流程档位: 轻量 | 标准 | 团队`
       - `> 收束间隔: N`  或  `> 收束节点: 功能点3后 / 功能点6后 / ...`
  2. 已完成功能点数跨过预设收束节点时，docs/reports/ 必须有相应数量的
     收束报告（收束报告-vX.Y.md）。到点未收束 → 闸门拦截（06 §2.1）。

没有 docs/plan/开发清单.md 的仓库视为非流程化项目（N/A），直接通过。

退出码:
    0 = 通过 / N/A
    1 = 闸门拦截（缺声明 或 到点未收束）

用法:
    python scripts/check_convergence_gate.py
    python scripts/check_convergence_gate.py --plan <path> --reports-dir <dir>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = REPO_ROOT / "docs" / "plan" / "开发清单.md"
DEFAULT_REPORTS = REPO_ROOT / "docs" / "reports"

DEFAULT_INTERVAL = 3  # 06 §2.2：收束间隔默认每 3 个功能点

TIER_RE = re.compile(r"流程档位[:：]\s*(轻量|标准|团队)")
INTERVAL_RE = re.compile(r"收束间隔[:：]\s*(\d+)")
NODES_RE = re.compile(r"收束节点[:：]\s*(.+)")
REPORT_RE = re.compile(r"^收束报告-v[\d.]+\.md$", re.IGNORECASE)


def count_completed(plan_text: str) -> int:
    """数已完成功能点：仅统计带 ✅ 的 markdown 表格行（| ... ✅ ... |），
    避免误数依赖图 / 图例 / 正文里的 ✅。"""
    n = 0
    for line in plan_text.splitlines():
        s = line.strip()
        if s.startswith("|") and "✅" in s:
            n += 1
    return n


def parse_thresholds(plan_text: str, completed: int) -> list[int]:
    """从头部声明推导收束节点阈值（功能点编号）列表。

    优先级：显式 `收束节点: 功能点N后` > `收束间隔: N` > 默认间隔 3。
    """
    nodes_m = NODES_RE.search(plan_text)
    if nodes_m:
        explicit = [int(x) for x in re.findall(r"功能点\s*(\d+)", nodes_m.group(1))]
        if explicit:
            return sorted(set(explicit))

    interval_m = INTERVAL_RE.search(plan_text)
    interval = int(interval_m.group(1)) if interval_m else DEFAULT_INTERVAL
    if interval <= 0:
        return []
    return list(range(interval, completed + 1, interval))


def count_reports(reports_dir: Path) -> int:
    """数 docs/reports/ 下的收束报告（收束报告-vX.Y.md）。"""
    if not reports_dir.exists():
        return 0
    return sum(
        1 for p in reports_dir.iterdir() if p.is_file() and REPORT_RE.match(p.name)
    )


def evaluate(plan_path: Path, reports_dir: Path) -> tuple[int, list[str]]:
    """返回 (退出码, 消息列表)。"""
    if not plan_path.exists():
        return 0, [f"N/A: {plan_path} 不存在（非流程化项目，跳过收束闸门）"]

    text = plan_path.read_text(encoding="utf-8")
    errors: list[str] = []

    # 1. 头部声明检查
    if not TIER_RE.search(text):
        errors.append(
            "开发清单.md 头部缺 `> 流程档位: 轻量 | 标准 | 团队` 声明（03 §1.0）"
        )
    if not INTERVAL_RE.search(text) and not NODES_RE.search(text):
        errors.append(
            "开发清单.md 头部缺 `> 收束间隔: N` 或 `> 收束节点: ...` 声明"
            "（03 §1.6 / 06 §2.1 硬闸门）"
        )

    # 2. 收束闸门：跨过的节点数必须有相应数量的收束报告
    completed = count_completed(text)
    thresholds = parse_thresholds(text, completed)
    crossed = [t for t in thresholds if t <= completed]
    reports = count_reports(reports_dir)
    if reports < len(crossed):
        errors.append(
            f"闸门拦截：已完成 {completed} 个功能点，跨过 {len(crossed)} 个收束节点 "
            f"{crossed}，但 docs/reports/ 只有 {reports} 份收束报告。"
            f"到点未收束 → 不得开始下一批功能点（06 §2.1）。"
        )

    if errors:
        return 1, errors
    return 0, [
        f"OK 收束闸门通过：完成={completed} 跨节点={len(crossed)} 收束报告={reports}"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="收束闸门 L1 检查（07-ai-workflow）")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS)
    args = parser.parse_args()

    code, messages = evaluate(args.plan, args.reports_dir)
    prefix = "FAIL 收束闸门：" if code else ""
    if code:
        print(prefix, file=sys.stderr)
        for m in messages:
            print(f"  - {m}", file=sys.stderr)
    else:
        for m in messages:
            print(m)
    return code


if __name__ == "__main__":
    sys.exit(main())
