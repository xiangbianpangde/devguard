#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_convergence_gate.py — commit-msg 钩子：收束硬闸门（V2.3 #52，节点驱动版）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段C + CLAUDE「收束节点（人触发）」。

**收束节点是设计阶段预先写定的里程碑，不是按完成数量的滚动阈值**（用户 2026-06-11 校正）。
到达预设节点时人触发收束（组内会议 → 优化/降熵 → 设计下一阶段 → 继续）。

机器可读标记（置于 STATUS.md）：
    <!-- convergence-gate: nodes=46,54 last_converged_fp=46 -->
  - nodes：设计阶段预设的收束节点（在该功能点编号之后必须收束才能继续下一阶段）
  - last_converged_fp：已执行收束覆盖到的最大功能点编号

判定（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. [skip-gate] → 放行（须在 meta/豁免清单.md 登记）
  2. 标记缺失 / 数据不可读 → 放行 + WARN（fail-open）
  3. next_node = 大于 last_converged_fp 的最小预设节点；无则放行（无待办收束节点）
  4. 仅当**本次提交把"已交付最大功能点编号"推到越过 next_node**
     （staged_max > next_node 且 staged_max > head_max）→ 拒提交。
     —— 即：跨过预设收束节点去交付下一阶段的功能点会被拦；批次内交付不拦。

释放节点 = 人触发收束后，上调 STATUS.md 标记的 last_converged_fp（≥ next_node）。

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
    r"<!--\s*convergence-gate:\s*nodes=([\d,\s]*?)\s+last_converged_fp=(\d+)\s*-->"
)


def parse_marker(text: str) -> tuple[list[int], int] | None:
    """解析收束闸门标记 → (预设节点列表, last_converged_fp)；无标记返回 None。"""
    m = MARKER.search(text)
    if not m:
        return None
    nodes = sorted(
        int(x) for x in m.group(1).replace(" ", "").split(",") if x.strip().isdigit()
    )
    return nodes, int(m.group(2))


def max_done_fp(plan_text: str) -> int:
    """开发清单里状态含 ✅ 的功能点的最大编号；无则 0。"""
    best = 0
    for line in plan_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].strip("*")
        if first.isdigit() and any("✅" in c for c in cells):
            best = max(best, int(first))
    return best


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
    nodes, last_fp = parsed

    pending = [n for n in nodes if n > last_fp]
    if not pending:
        print(f"OK 收束闸门通过（无待办收束节点；已收束至 #{last_fp}）")
        return 0
    next_node = min(pending)

    staged_plan = git_show(f":{PLAN_REL}")
    if staged_plan is None:
        pp = REPO_ROOT / PLAN_REL
        staged_plan = pp.read_text(encoding="utf-8") if pp.exists() else ""
    head_plan = git_show(f"HEAD:{PLAN_REL}") or ""

    staged_max = max_done_fp(staged_plan)
    head_max = max_done_fp(head_plan)

    if staged_max > next_node and staged_max > head_max:
        print("FAIL 收束硬闸门拦截：", file=sys.stderr)
        print(
            f"  交付功能点 #{staged_max} 越过设计时收束节点 #{next_node}"
            f"（已收束至 #{last_fp}）",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            f"  须先在 #{next_node} 处收束（人触发：组内会议→优化降熵→设计下阶段）",
            file=sys.stderr,
        )
        print(
            f"  收束后上调 STATUS.md 标记 last_converged_fp ≥ {next_node} 即释放。",
            file=sys.stderr,
        )
        print("  豁免: 末尾加 [skip-gate]（须登记 meta/豁免清单.md）", file=sys.stderr)
        return 1

    print(f"OK 收束闸门通过（已交付最大 #{staged_max} 未越过下一节点 #{next_node}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
