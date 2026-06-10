#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_worklog_structure.py — commit-msg 钩子：worklog 内容结构校验
============================================================
依据：docs/templates/worklog模板.md + 流程强制化方案 #38

校验本次提交 staged 的每个顶层 worklog（worklogs/<date>_*.md）：
  必需段（硬拦，按概念同义匹配模板 + 实际用法两种写法）：
    - 完成内容：标题含「做了什么」或「完成了什么」
    - 验证结果：标题含「验证」（验证结果 / 验证）
    - 交接/下一步：标题含「下一步」或「交接」或「给下一位」
  完成项（硬拦）：
    - 至少 1 个 `- [x]` 勾选项（证明确有落地的完成项，不只是叙述）
  推荐段（软提示，不拦——模板标记为可选）：
    - 关键决策 / 遇到的问题

> 模板（docs/templates/worklog模板.md）必填三段为
> 「做了什么 / 验证结果 / 给下一位的交接」；本钩子以此为硬约束基线，
> 并把 `- [x]` 完成项纳入硬约束（方案 #38）。决策/问题段保持可选。

判定：
  1. commit message 含 [skip-worklog-structure] → 放行
  2. 无 staged 顶层 worklog → 放行
  3. 任一 staged worklog 缺必需段或缺完成项 → FAIL

用法（pre-commit 框架调用）:
    python scripts/check_worklog_structure.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_MARKER = "[skip-worklog-structure]"

WORKLOG_RE = re.compile(r"^worklogs/(\d{4}-\d{2}-\d{2})[_\-\.].+\.md$", re.IGNORECASE)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[x\]", re.IGNORECASE | re.MULTILINE)

# 必需段：概念 -> 任一同义关键词命中标题行即算满足
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "完成内容（做了什么/完成了什么）": ["做了什么", "完成了什么", "完成内容"],
    "验证结果": ["验证"],
    "交接/下一步": ["下一步", "交接", "给下一位"],
}
# 推荐段（软提示）
RECOMMENDED_SECTIONS: dict[str, list[str]] = {
    "关键决策": ["关键决策", "决策"],
    "遇到的问题": ["遇到的问题", "问题"],
}


def staged_worklogs() -> list[str]:
    """本次 staged 的顶层 worklog 路径列表"""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    files: list[str] = []
    for line in out.splitlines():
        p = line.strip().replace("\\", "/")
        if p and WORKLOG_RE.match(p):
            files.append(p)
    return files


def staged_content(path: str) -> str:
    """读 staged 版本内容（git show :path），失败退回工作区文件"""
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


def heading_lines(content: str) -> list[str]:
    """取所有 markdown 标题行（## 开头）"""
    return [ln for ln in content.splitlines() if ln.lstrip().startswith("#")]


def check_one(path: str) -> tuple[list[str], list[str]]:
    """返回 (errors, warnings)"""
    content = staged_content(path)
    headings = "\n".join(heading_lines(content))
    errors: list[str] = []
    warnings: list[str] = []

    for concept, keywords in REQUIRED_SECTIONS.items():
        if not any(k in headings for k in keywords):
            errors.append(f"{path}: 缺必需段「{concept}」")

    if not CHECKBOX_RE.search(content):
        errors.append(f"{path}: 缺至少 1 个 `- [x]` 完成项")

    for concept, keywords in RECOMMENDED_SECTIONS.items():
        if not any(k in headings for k in keywords):
            warnings.append(f"{path}: 建议补充「{concept}」段")

    return errors, warnings


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "用法: python check_worklog_structure.py <commit_msg_file>", file=sys.stderr
        )
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-worklog-structure]，跳过 worklog 结构检查")
        return 0

    worklogs = staged_worklogs()
    if not worklogs:
        return 0

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for wl in worklogs:
        errs, warns = check_one(wl)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for w in all_warnings:
        print(f"WARN {w}")

    if all_errors:
        print("FAIL worklog 结构校验不通过：", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  模板: docs/templates/worklog模板.md", file=sys.stderr)
        print("  豁免: commit message 末尾加 [skip-worklog-structure]", file=sys.stderr)
        return 1

    print(f"OK worklog 结构校验通过（{len(worklogs)} 个 worklog）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
