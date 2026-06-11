#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_convergence_gate.py — commit-msg 钩子：收束硬闸门（V2.3 #52）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段C + CLAUDE「收束节点（人触发）」。
把"每 N 个功能点必须回头收束"从 AI 自律（软闸门）升级为提交时工具硬拦。

机器可读标记（置于 STATUS.md）：
    <!-- convergence-gate: last_converged_fp=46 threshold=3 -->
  - last_converged_fp：上次收束节点覆盖到的最大功能点编号
  - threshold：允许的"未收束已完成功能点"上限（默认 3）

判定（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. [skip-gate] → 放行（须在 meta/豁免清单.md 登记）
  2. 标记缺失 / 数据不可读 → 放行 + WARN（fail-open，闸门未生效）
  3. 计算 staged 与 HEAD 两版开发清单里"编号 > last_converged_fp 且状态 ✅"的功能点数；
     仅当 **本次提交把该数推过阈值**（staged > threshold 且 staged > head）→ 拒提交。
     —— 故非交付提交（不新增完成项）永不被拦，仓库不被冻结。

释放闸门 = 人触发收束四阶段后，上调 STATUS.md 标记的 last_converged_fp + 收束历史加行。

用法（pre-commit 框架调用）:
    python scripts/check_convergence_gate.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_REL = "STATUS.md"
PLAN_REL = "docs/plan/开发清单.md"
SKIP_MARKER = "[skip-gate]"

MARKER = re.compile(
    r"<!--\s*convergence-gate:\s*last_converged_fp=(\d+)\s+threshold=(\d+)\s*-->"
)


def parse_marker(text: str) -> tuple[int, int] | None:
    m = MARKER.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def unconverged_done(plan_text: str, last_fp: int) -> int:
    """开发清单里 编号 > last_fp 且状态含 ✅ 的功能点行数。"""
    count = 0
    for line in plan_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].strip("*")
        if not first.isdigit():
            continue
        if int(first) > last_fp and any("✅" in c for c in cells):
            count += 1
    return count


def git_show(ref_path: str) -> str | None:
    """git show <ref:path>；失败返回 None。"""
    try:
        return subprocess.run(
            ["git", "show", ref_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "用法: python check_convergence_gate.py <commit_msg_file>", file=sys.stderr
        )
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-gate]，跳过收束闸门")
        return 0

    # 标记从 staged STATUS 读（让收束提交在同次生效）；取不到回退工作区
    status_text = git_show(f":{STATUS_REL}")
    if status_text is None:
        sp = REPO_ROOT / STATUS_REL
        status_text = sp.read_text(encoding="utf-8") if sp.exists() else ""
    parsed = parse_marker(status_text)
    if parsed is None:
        print("WARN 未找到收束闸门标记（convergence-gate），闸门未生效")
        return 0
    last_fp, threshold = parsed

    staged_plan = git_show(f":{PLAN_REL}")
    if staged_plan is None:
        pp = REPO_ROOT / PLAN_REL
        staged_plan = pp.read_text(encoding="utf-8") if pp.exists() else ""
    head_plan = git_show(f"HEAD:{PLAN_REL}") or ""

    staged_count = unconverged_done(staged_plan, last_fp)
    head_count = unconverged_done(head_plan, last_fp)

    if staged_count > threshold and staged_count > head_count:
        print("FAIL 收束硬闸门拦截：", file=sys.stderr)
        print(
            f"  距上次收束（功能点 #{last_fp}）已完成 {staged_count} 个功能点，"
            f"超过阈值 {threshold}",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            "  收束为人触发的四阶段（整理/测试/审计/验证）→ ADR + 收束报告；",
            file=sys.stderr,
        )
        print(
            "  完成后上调 STATUS.md 的 last_converged_fp + 收束历史加行即释放。",
            file=sys.stderr,
        )
        print("  豁免: 末尾加 [skip-gate]（须登记 meta/豁免清单.md）", file=sys.stderr)
        return 1

    print(
        f"OK 收束闸门通过（未收束已完成 {staged_count} ≤ 阈值 {threshold}，"
        f"基线 #{last_fp}）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
