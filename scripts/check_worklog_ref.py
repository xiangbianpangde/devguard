#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_worklog_ref.py — commit-msg 钩子：commit message 必须引用 worklog 文件
============================================================
红线依据：06-documentation §2.5 + 03-git §一 红线（人记得 + 工具拦）
"汇报不断档"——每 commit 必带 worklogs/YYYY-MM-DD_*.md 引用

用法（pre-commit 框架调用）:
    python scripts/check_worklog_ref.py <commit_msg_file>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# worklog 引用模式：worklogs/YYYY-MM-DD_*.md
# 允许 (a) 完整路径 (b) 相对路径 (c) 只文件名 (d) 链接 [text](path)
WORKLOG_PATTERN = re.compile(
    r"worklogs[\\/]+\d{4}-\d{2}-\d{2}[_\-\w]*\.md",
    re.IGNORECASE,
)


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_worklog_ref.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg_file = Path(sys.argv[1])
    if not msg_file.exists():
        print(f"FAIL: commit-msg 文件不存在: {msg_file}", file=sys.stderr)
        return 1

    msg = msg_file.read_text(encoding="utf-8").strip()
    # commit-msg 第一行（subject）可能不包含；body 必含
    # 整段 commit message 至少要有 1 处 worklog 引用
    if WORKLOG_PATTERN.search(msg):
        return 0

    print("FAIL: commit message 必须引用 worklog 文件（红线 6）", file=sys.stderr)
    print("", file=sys.stderr)
    print("格式: worklogs/YYYY-MM-DD_<描述>.md", file=sys.stderr)
    print(
        "示例: feat(xxx): 实现功能（详见 worklogs/2026-06-07_xxx.md）", file=sys.stderr
    )
    print("", file=sys.stderr)
    print(
        "豁免: 在 commit message 末尾加 [skip-worklog] 标记（仅收束节点 / 紧急 hotfix 用）",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
