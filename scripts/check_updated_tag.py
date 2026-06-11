#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_updated_tag.py — commit-msg 钩子：「更新时间」标签强制化（V2.3 #53）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段B
"部分文件缺「更新」标签 / 有标签的文件提交时不强制刷新" → 工具焊死。

受管文件（MANAGED）= 入口/索引类文档，必须携带 `> 更新: YYYY-MM-DD` 标签，
且**本次提交一旦改动该文件，标签日期必须是今天**（强制刷新更新时间）。

判定逻辑（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. commit message 含 [skip-updated] → 放行（豁免须在 meta/豁免清单.md 登记）
  2. 取本次 staged 的受管文件；无 → 放行
  3. 任一 staged 受管文件：
     a. 缺 `> 更新: YYYY-MM-DD` 标签 → FAIL
     b. 标签日期 ≠ 今天 → FAIL（提交受管文件必须刷新更新时间）

> 与 PostToolUse 阻断钩子（scripts/hook_updated_tag_posttooluse.py）+ 豁免登记（#51）
> 共同构成"编辑当下阻断 + 提交时硬拦 + 豁免留痕"的组合样板（设计 §3.3 阶段B）。

用法（pre-commit 框架调用）:
    python scripts/check_updated_tag.py <commit_msg_file>
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_MARKER = "[skip-updated]"

# 受管文件：必须携带并刷新「更新」标签的入口/索引类文档（正斜杠相对路径）
MANAGED: set[str] = {
    "STATUS.md",
    "CLAUDE.md",
    "README.md",
    "docs/plan/开发清单.md",
    "meta/FILE_GRAPH.md",
    "meta/豁免清单.md",
}

# `> 更新: 2026-06-11...` 或全角冒号；取第一处日期
UPDATE_TAG = re.compile(r"^>\s*更新[:：]\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def extract_update_date(content: str) -> str | None:
    """从文件内容抽出「更新」标签日期（YYYY-MM-DD），无则 None。"""
    m = UPDATE_TAG.search(content)
    return m.group(1) if m else None


def staged_managed_files() -> list[str]:
    """本次 staged 且属于 MANAGED 的文件路径列表。"""
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    staged = {ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()}
    return sorted(staged & MANAGED)


def staged_content(path: str) -> str:
    """读 staged 版本（git show :path），失败退回工作区文件。"""
    try:
        return subprocess.run(
            ["git", "show", f":{path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        fp = REPO_ROOT / path
        return fp.read_text(encoding="utf-8") if fp.exists() else ""


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_updated_tag.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-updated]，跳过「更新」标签刷新检查")
        return 0

    files = staged_managed_files()
    if not files:
        return 0

    today = datetime.date.today().isoformat()
    errors: list[str] = []
    for path in files:
        date = extract_update_date(staged_content(path))
        if date is None:
            errors.append(f"{path}: 缺 `> 更新: YYYY-MM-DD` 标签")
        elif date != today:
            errors.append(
                f"{path}: 「更新」标签日期 {date} ≠ 今天 {today}（提交受管文件须刷新）"
            )

    if errors:
        print("FAIL「更新时间」标签校验不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"  修复: 把对应文件顶部 `> 更新:` 改成今天 {today}", file=sys.stderr)
        print(
            "  豁免: 末尾加 [skip-updated]（须登记 meta/豁免清单.md）", file=sys.stderr
        )
        return 1

    print(f"OK「更新」标签校验通过（{len(files)} 个受管文件，均为今天 {today}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
