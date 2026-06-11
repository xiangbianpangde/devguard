#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_file_placement.py — 新增文件路径是否符合 FILE_GRAPH 决策树（V2.1 #45 / 叶子级强化）
============================================================
依据：meta/FILE_GRAPH.md §一 目录树 + §三 决策树 + 核心规则 1「新增文件前必查 FILE_GRAPH」

检查本次提交新增的文件（`git diff --cached --name-only --diff-filter=A`）：
  1. 根目录禁止放散文件（只允许既定入口白名单）——硬拦
  2. 叶子级校验：文件必须落在 FILE_GRAPH 认可的区域里——硬拦
       - 已知顶层区（conventions/ src/ worklogs/ scripts/ meta/ tests/ .github/ .claude/）
         内部**自由嵌套**（示例代码分层、模板分组、调研子树等都合法）；
       - docs/ 必须落在已知子区目录下：docs/<plan|reports|research|specs|templates|历史文件>/…；
         直接挂在 docs/ 根下的散文件、未知 docs 子区、未知顶层区 → 拦。
     —— 较旧版「顶层前缀软 WARN」更严：不再允许把文件丢进未登记的区域。

豁免：[skip-file-placement] 在 commit message 中（新增结构节点时先更新 FILE_GRAPH 再豁免提交）。

用法（commit-msg hook）:
    python scripts/check_file_placement.py <commit_msg_file>

模型（ROOT_WHITELIST / FREE_TOP_AREAS / DOCS_SUBSECTIONS / placement_error）供
audit_file_placement.py 复用。
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
    "CODEOWNERS",
    ".markdownlintignore",
}

# 已知顶层区——内部自由嵌套（示例分层 / 模板分组 / 调研子树 / 配置树等均合法）
FREE_TOP_AREAS = {
    "conventions",
    "src",
    "worklogs",
    "scripts",
    "meta",
    "tests",
    ".github",
    ".claude",
}

# docs/ 下认可的子区——文件须落在 docs/<子区>/… 内，不接受直挂 docs/ 根的散文件
DOCS_SUBSECTIONS = {
    "plan",
    "reports",
    "research",
    "specs",
    "templates",
    "历史文件",
}


def is_in_root(path: str) -> bool:
    return "/" not in path


def placement_error(path: str) -> str | None:
    """返回违规说明；合法返回 None。"""
    if is_in_root(path):
        if path not in ROOT_WHITELIST:
            return (
                f"根目录新增散文件「{path}」（不在白名单中）。"
                f"请按 meta/FILE_GRAPH.md 决策树放入对应子目录。"
            )
        return None

    seg = path.split("/")
    top = seg[0]

    if top in FREE_TOP_AREAS:
        return None

    if top == "docs":
        # 必须落在已知子区目录下：docs/<子区>/<...>
        if len(seg) >= 3 and seg[1] in DOCS_SUBSECTIONS:
            # plan 子区下 design/ 是 7 件套设计文件夹，允许 docs/plan/design/<设计名>/*
            if seg[1] == "plan" and seg[2] == "design":
                return None
            return None
        if len(seg) == 2:
            return (
                f"docs/ 根下散文件「{path}」——应放进子区"
                f"（{'/'.join(sorted(DOCS_SUBSECTIONS))}）之一。"
            )
        return (
            f"「{path}」的 docs 子区 `{seg[1]}` 未登记，"
            f"请放入已知子区或先更新 meta/FILE_GRAPH.md。"
        )

    if top == "docs/plan":
        # docs/plan/<子区>/ 自由嵌套（plan 是已知子区）
        return None

    return (
        f"「{path}」位于未登记的顶层区 `{top}/`。"
        f"请放入既有区域，或先更新 meta/FILE_GRAPH.md 与本脚本 FREE_TOP_AREAS。"
    )


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

    errors = [e for f in new_files if (e := placement_error(f))]

    if errors:
        print("FAIL 文件放置检查不通过（叶子级）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  依据: meta/FILE_GRAPH.md §一 目录树 + §三 决策树", file=sys.stderr)
        print(
            "  修复: 移入认可目录（conventions/ docs/ src/ worklogs/"
            " scripts/ meta/ tests/ .github/）",
            file=sys.stderr,
        )
        print(
            "  新结构: 若确需新目录节点，先更新 meta/FILE_GRAPH.md + 本脚本 VALID_DIRS，再提交",
            file=sys.stderr,
        )
        print("  豁免: commit message 末尾加 [skip-file-placement]", file=sys.stderr)
        return 1

    print(f"OK 文件放置检查通过（{len(new_files)} 个新文件，叶子级）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
