#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_file_placement.py — 新增文件路径是否符合 FILE_GRAPH 决策树（V2.1 #45）
============================================================
依据：meta/FILE_GRAPH.md §三 决策树 + 核心规则 1「新增文件前必查 FILE_GRAPH」

检查本次提交新增的文件（`git diff --cached --name-only --diff-filter=A`）：
  1. 根目录禁止放散文件（只允许既定入口：CLAUDE.md / README.md / STATUS.md /
     dashboard.html / .gitignore / .pre-commit-config.yaml 等）
  2. 文件路径是否命中 FILE_GRAPH 定义的任一合法目录节点（软提示 WARN）
     —— 不硬拦，因为决策树是启发式规则，人工判断优先

豁免：[skip-file-placement] 在 commit message 中。

用法（commit-msg hook）:
    python scripts/check_file_placement.py <commit_msg_file>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_MARKER = "[skip-file-placement]"

# 根目录白名单——这些文件可以合法放在仓库根
ROOT_WHITELIST = {
    "CLAUDE.md",
    "README.md",
    "STATUS.md",
    "dashboard.html",
    ".gitignore",
    ".gitattributes",
    ".gitmessage",
    ".editorconfig",
    ".pre-commit-config.yaml",
    "commitlint.config.js",
    ".spectral.yaml",
    ".gitleaks.toml",
    ".markdownlint.json",
    "importlinter.ini",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "CHANGELOG.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "CODEOWNERS",  # .github/CODEOWNERS 正确路径
}

# FILE_GRAPH 定义的合法目录前缀（第一级目录）
ALLOWED_TOP_DIRS = {
    "conventions/",
    "docs/",
    "docs/plan/",
    "docs/plan/design/",
    "docs/reports/",
    "docs/research/",
    "docs/specs/",
    "docs/templates/",
    "docs/templates/devguard/",
    "src/",
    "src/architecture/",
    "src/coding/",
    "src/git/",
    "src/api/",
    "src/testing/",
    "src/documentation/",
    "src/code-understanding/",
    "worklogs/",
    "worklogs/decisions/",
    "scripts/",
    "meta/",
    ".github/",
    ".github/workflows/",
    "tests/",
    "tests/conventions/",
    ".claude/",
}


def staged_new_files() -> list[str]:
    """Return staged new files (normalized to forward-slash paths)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
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


def is_in_root(path: str) -> bool:
    """True if path has no directory separator (is a root-level file)."""
    return "/" not in path


def matches_any_prefix(path: str, prefixes: set[str]) -> bool:
    """True if path starts with any of the allowed directory prefixes."""
    return any(path.startswith(p) for p in prefixes)


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python check_file_placement.py <commit_msg_file>", file=sys.stderr)
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-file-placement]，跳过文件放置检查")
        return 0

    new_files = staged_new_files()
    if not new_files:
        return 0

    errors: list[str] = []
    warnings: list[str] = []

    for f in new_files:
        # Rule 1: root-level stray files
        if is_in_root(f):
            basename = f
            if basename not in ROOT_WHITELIST:
                errors.append(
                    f"根目录新增散文件「{f}」（不在白名单中）。"
                    f"请按 meta/FILE_GRAPH.md 决策树放入对应子目录。"
                )
            continue

        # Rule 2: does it match any FILE_GRAPH category? (soft WARN)
        if not matches_any_prefix(f, ALLOWED_TOP_DIRS):
            warnings.append(
                f"「{f}」的路径前缀不在 FILE_GRAPH 已知目录节点中，"
                f"请确认放置正确（见 meta/FILE_GRAPH.md §三决策树）"
            )

    for w in warnings:
        print(f"WARN {w}")

    if errors:
        print("FAIL 文件放置检查不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  依据: meta/FILE_GRAPH.md §三 决策树——根目录禁止堆散文件", file=sys.stderr
        )
        print(
            "  修复: 将文件移入对应子目录（conventions/ docs/ src/ worklogs/ scripts/ meta/）",
            file=sys.stderr,
        )
        print("  豁免: commit message 末尾加 [skip-file-placement]", file=sys.stderr)
        return 1

    print(f"OK 文件放置检查通过（{len(new_files)} 个新文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
