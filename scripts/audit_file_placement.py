#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_file_placement.py — 全树文件放置审计（V2.1 #45 配套）
============================================================
依据：meta/FILE_GRAPH.md。与 commit-msg 钩子 check_file_placement.py 共用同一目录模型，
区别在于：钩子只看本次提交新增文件，本脚本扫**整棵仓库树**，揪出存量散乱文件。

扫描范围：`git ls-files` + `git ls-files --others --exclude-standard`
         （已跟踪 + 未跟踪但未被 .gitignore 忽略；自动跳过 .git/ 与忽略项）

用法:
    python scripts/audit_file_placement.py          # 报告；有违规 → 退出码 1
    python scripts/audit_file_placement.py --quiet  # 仅在有违规时输出

退出码: 0 = 全部合规；1 = 存在违规（供 CI 使用）
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_file_placement import placement_error  # noqa: E402


def all_repo_files() -> list[str]:
    """已跟踪 + 未跟踪未忽略文件（forward-slash，去重排序）。"""
    files: set[str] = set()
    for args in (
        ["git", "ls-files"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        try:
            out = subprocess.run(
                args, capture_output=True, text=True, encoding="utf-8", check=True
            ).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        for line in out.splitlines():
            p = line.strip().replace("\\", "/")
            if p:
                files.add(p)
    return sorted(files)


def main() -> int:
    quiet = "--quiet" in sys.argv[1:]
    files = all_repo_files()
    violations = [(f, e) for f in files if (e := placement_error(f))]

    if violations:
        print(f"FAIL 全树文件放置审计：{len(violations)} 个违规 / 共 {len(files)} 文件")
        for f, e in violations:
            print(f"  - {e}")
        print("")
        print("  依据: meta/FILE_GRAPH.md §一 目录树 + §三 决策树")
        print(
            "  修复: 移入认可目录，或更新 FILE_GRAPH + check_file_placement.VALID_DIRS"
        )
        return 1

    if not quiet:
        print(f"OK 全树文件放置审计通过（{len(files)} 个文件全部合规）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
