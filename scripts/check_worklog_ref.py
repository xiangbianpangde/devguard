#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_worklog_ref.py — commit-msg 钩子：commit message 必须引用 worklog 文件
                       且该 worklog 文件必须在本次提交的变更中真实存在
============================================================
红线依据：06-documentation §2.5 + 03-git §一 红线（人记得 + 工具拦）
"汇报不断档"——每 commit 必带 worklogs/YYYY-MM-DD_*.md 引用

V2.1 #36 增强：在原有"commit message 含 worklog 引用"正则匹配基础上，
增加 `git diff --cached --name-only` 交叉比对——验证 commit message 引用的
worklog 文件**真实在本次提交的 staged 变更中**，而非只在文字里提一句。

判定逻辑：
  1. commit message 含 [skip-worklog] → 直接放行（收束节点 / 紧急 hotfix）
  2. commit message 无任何 worklog 引用 → FAIL（原有行为）
  3. 有引用，但引用的 worklog 文件没出现在 staged 变更里 → FAIL（V2.1 新增）
  4. 有引用且引用的 worklog 文件在 staged 变更里 → PASS

用法（pre-commit 框架调用）:
    python scripts/check_worklog_ref.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# worklog 引用模式：worklogs/YYYY-MM-DD_*.md
# 允许 (a) 完整路径 (b) 相对路径 (c) 只文件名 (d) 链接 [text](path)
WORKLOG_PATTERN = re.compile(
    r"worklogs[\\/]+(\d{4}-\d{2}-\d{2}[_\-\w.]*\.md)",
    re.IGNORECASE,
)

SKIP_MARKER = "[skip-worklog]"


def staged_worklog_basenames() -> set[str]:
    """返回本次提交 staged 变更中所有 worklog 文件的 basename（小写）

    用 `git diff --cached --name-only` 取 staged 文件；只保留 worklogs/ 下的 .md。
    git 失败（非仓库 / 无 git）时返回空集——交由上层判 FAIL（保守拦截）。
    """
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()

    names: set[str] = set()
    for line in out.splitlines():
        p = line.strip().replace("\\", "/")
        if not p:
            continue
        # 只认 worklogs/ 目录下的 .md
        if re.match(r"worklogs/.+\.md$", p, re.IGNORECASE):
            names.add(Path(p).name.lower())
    return names


def referenced_worklog_basenames(msg: str) -> set[str]:
    """从 commit message 抽出所有引用的 worklog basename（小写）"""
    return {m.lower() for m in WORKLOG_PATTERN.findall(msg)}


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_worklog_ref.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg_file = Path(sys.argv[1])
    if not msg_file.exists():
        print(f"FAIL: commit-msg 文件不存在: {msg_file}", file=sys.stderr)
        return 1

    msg = msg_file.read_text(encoding="utf-8").strip()

    # 1. 豁免标记：收束节点 / 紧急 hotfix 放行
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-worklog]，跳过 worklog 引用检查")
        return 0

    # 2. 必须含 worklog 引用
    referenced = referenced_worklog_basenames(msg)
    if not referenced:
        print(
            "FAIL: commit message 必须引用 worklog 文件（汇报不断档）", file=sys.stderr
        )
        print("", file=sys.stderr)
        print("格式: worklogs/YYYY-MM-DD_<描述>.md", file=sys.stderr)
        print(
            "示例: feat(xxx): 实现功能（详见 worklogs/2026-06-07_xxx.md）",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            "豁免: 在 commit message 末尾加 [skip-worklog]（仅收束节点 / 紧急 hotfix 用）",
            file=sys.stderr,
        )
        return 1

    # 3. V2.1 #36：引用的 worklog 必须真实在 staged 变更中
    staged = staged_worklog_basenames()
    if referenced & staged:
        return 0

    print(
        "FAIL: commit message 引用了 worklog，但该文件未出现在本次提交的变更中",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    print(f"  引用的 worklog: {sorted(referenced)}", file=sys.stderr)
    print(
        f"  本次 staged 的 worklog: {sorted(staged) if staged else '（无）'}",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    print(
        "修复: 把对应的 worklog 文件 `git add` 进本次提交，或修正 commit message 中的文件名",
        file=sys.stderr,
    )
    print(
        "豁免: 在 commit message 末尾加 [skip-worklog]（仅收束节点 / 紧急 hotfix 用）",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
