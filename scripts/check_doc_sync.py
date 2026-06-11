#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_doc_sync.py — commit-msg 钩子：四件套文档硬同步（V2.3 阶段C 补遗，#52 拆出项）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段C + §1.4 分粒度耦合
"四件套(worklog/STATUS/开发清单/CLAUDE)只有 worklog→STATUS 一条边被焊死" → 补边。

分粒度（§1.4：过紧耦合会让强制烂掉）：
  - **结构性改动（新增/删除编号功能点行）→ 硬拦**：
      STATUS.md 与 docs/plan/开发清单.md 的编号功能点集合，本次提交引入的
      增/删必须两边同步；且发生结构性改动时 CLAUDE.md（当前状态）必须同提交。
  - **值改动（改状态/日期，行集不变）→ 仅 WARN**：
      只把 ⏳ 翻 ✅ 不强制连改 CLAUDE/清单——避免噪音逼出豁免滥用。

判定逻辑（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. [skip-docsync] → 放行（豁免须登记 meta/豁免清单.md）
  2. 取 staged/HEAD 两版 STATUS 与 开发清单 的编号功能点集合（行首 `| #N` / `| N |`）
     —— 只比对**本次提交引入的增量**，不追溯历史口径差（避免存量差异冻结仓库）
  3. STATUS 新增 #N 而暂存后清单无 #N（或反向）→ FAIL
     STATUS 删除 #N 而暂存后清单仍有 #N（或反向）→ FAIL
     发生任一结构性增删而 CLAUDE.md 未 staged → FAIL
  4. STATUS staged 但行集无变化且清单未同 staged → WARN（值级改动提醒）

> 注：1-35 号历史行在 STATUS 详细列表中无编号（fp 标签口径），不参与本检查；
>     编号行（#36 起）是两文件共同的机器可读键。

用法（pre-commit 框架调用）:
    python scripts/check_doc_sync.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_REL = "STATUS.md"
PLAN_REL = "docs/plan/开发清单.md"
CLAUDE_REL = "CLAUDE.md"
SKIP_MARKER = "[skip-docsync]"

# STATUS 详细列表行：首单元格以 #N 开头；开发清单行：首单元格是纯数字
STATUS_FP_RE = re.compile(r"^\|\s*\*{0,2}#(\d+)\b")
PLAN_FP_RE = re.compile(r"^\|\s*(\d+)\s*\|")


def staged_files() -> set[str]:
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    return {ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()}


def git_show(ref_path: str) -> str | None:
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


def content_at(path: str, staged: bool) -> str:
    """staged=True 取 index 版本，否则取 HEAD 版本；都取不到回退工作区/空串。"""
    ref = f":{path}" if staged else f"HEAD:{path}"
    text = git_show(ref)
    if text is not None:
        return text
    fp = REPO_ROOT / path
    return fp.read_text(encoding="utf-8") if fp.exists() else ""


def status_fps(text: str) -> set[int]:
    """STATUS.md 中编号功能点行（| #N …）的编号集合。"""
    out: set[int] = set()
    for line in text.splitlines():
        m = STATUS_FP_RE.match(line.strip())
        if m:
            out.add(int(m.group(1)))
    return out


def plan_fps(text: str) -> set[int]:
    """开发清单中编号功能点行（| N | …）的编号集合。"""
    out: set[int] = set()
    for line in text.splitlines():
        m = PLAN_FP_RE.match(line.strip())
        if m:
            out.add(int(m.group(1)))
    return out


def sync_errors(
    s_head: set[int],
    s_staged: set[int],
    p_head: set[int],
    p_staged: set[int],
    claude_staged: bool,
) -> tuple[list[str], bool]:
    """返回 (errors, structural_change)。只看本次提交引入的增量。"""
    errors: list[str] = []
    added_s, removed_s = s_staged - s_head, s_head - s_staged
    added_p, removed_p = p_staged - p_head, p_head - p_staged
    structural = bool(added_s or removed_s or added_p or removed_p)

    if miss := sorted(added_s - p_staged):
        errors.append(f"STATUS 新增功能点 {miss}，但开发清单（暂存后）没有对应行")
    if miss := sorted(added_p - s_staged):
        errors.append(f"开发清单新增功能点 {miss}，但 STATUS（暂存后）没有对应行")
    if lin := sorted(removed_s & p_staged):
        errors.append(f"STATUS 删除了功能点 {lin}，但开发清单（暂存后）仍保留")
    if lin := sorted(removed_p & s_staged):
        errors.append(f"开发清单删除了功能点 {lin}，但 STATUS（暂存后）仍保留")

    if structural and not claude_staged:
        errors.append(
            "发生功能点行增/删（结构性改动），但 CLAUDE.md 未同提交"
            "（核心规则：新增功能点 → STATUS + 开发清单 + CLAUDE 当前状态同步）"
        )
    return errors, structural


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_doc_sync.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-docsync]，跳过四件套同步检查")
        return 0

    staged = staged_files()
    status_in = STATUS_REL in staged
    plan_in = PLAN_REL in staged
    if not status_in and not plan_in:
        return 0  # 未动两件套，零摩擦

    s_head = status_fps(content_at(STATUS_REL, staged=False))
    s_staged = status_fps(content_at(STATUS_REL, staged=status_in))
    p_head = plan_fps(content_at(PLAN_REL, staged=False))
    p_staged = plan_fps(content_at(PLAN_REL, staged=plan_in))

    errors, structural = sync_errors(
        s_head, s_staged, p_head, p_staged, CLAUDE_REL in staged
    )

    if errors:
        print("FAIL 四件套文档同步检查不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  依据: CLAUDE.md 核心规则 3 + 设计 v2.3 §3.3 阶段C", file=sys.stderr)
        print(
            "  豁免: 末尾加 [skip-docsync]（须登记 meta/豁免清单.md）", file=sys.stderr
        )
        return 1

    if status_in and not structural and not plan_in:
        print("WARN STATUS 值级改动未同步开发清单（仅提醒；结构性增删才硬拦）")
    if structural:
        print("OK 四件套同步检查通过（结构性改动两侧一致 + CLAUDE 已同步）")
    else:
        print("OK 四件套同步检查通过（无结构性增删）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
