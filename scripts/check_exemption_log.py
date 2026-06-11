#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_exemption_log.py — commit-msg 钩子：豁免登记强制化（V2.3 #51）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段A
"豁免一旦散落、零登记，强制就名存实亡" —— 把豁免从隐式绕过升级为显式留痕 + 可审计。

判定逻辑（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. commit message 不含任何 [skip-*] 标记 → PASS（绝大多数提交，零摩擦）
  2. 含 [skip-*] 标记：
     a. 每个标记必须在 meta/豁免清单.md §二 已登记（未登记标记 → FAIL）
     b. 本次提交必须把 meta/豁免清单.md 一起 staged（强制追加使用记录 → FAIL if 未 staged）
  3. 本钩子自身不可豁免（它是登记器，没有 [skip-exemption]）

附加用法：
  python scripts/check_exemption_log.py --audit   # 扫 git 历史，汇总 [skip-*] 使用 vs 已登记标记

用法（pre-commit 框架调用）:
    python scripts/check_exemption_log.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "meta" / "豁免清单.md"
REGISTRY_REL = "meta/豁免清单.md"

# 豁免标记：[skip-xxx]（字母/数字/连字符）。本钩子自身的 [skip-exemption] 不存在，故不特判。
SKIP_MARKER = re.compile(r"\[skip-[\w-]+\]")


def extract_skip_markers(msg: str) -> set[str]:
    """从 commit message 抽出所有 [skip-*] 豁免标记（原样，含方括号）。"""
    return set(SKIP_MARKER.findall(msg))


def registry_markers() -> set[str]:
    """meta/豁免清单.md §二 目录里已登记的合法豁免标记集合。

    只认 markdown 表格行的首列恰为 [skip-*] 的条目（= §二 标记目录表），
    刻意不扫散文 / §三 使用记录列——避免把散文提到的未来标记或 "不存在的
    [skip-exemption]" 误当成已登记。清单不存在时返回空集（上层判 FAIL）。
    """
    if not REGISTRY.exists():
        return set()
    cell_marker = re.compile(r"^\[skip-[\w-]+\]$")
    markers: set[str] = set()
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        first_cell = line.strip().strip("|").split("|")[0].strip().strip("`")
        if cell_marker.match(first_cell):
            markers.add(first_cell)
    return markers


def staged_files() -> set[str]:
    """本次提交 staged 的文件路径集合（正斜杠规范化）。

    用 core.quotepath=false 让 git 输出未转义的 UTF-8 中文路径（豁免清单.md）。
    git 失败时返回空集——交由上层判 FAIL（保守拦截）。
    """
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
    return {
        line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()
    }


def audit() -> int:
    """扫 git 历史里所有 [skip-*] 使用，对比已登记标记，打印汇总（非阻断）。"""
    try:
        out = subprocess.run(
            ["git", "log", "--format=%B"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"WARN 无法读取 git 历史: {e}", file=sys.stderr)
        return 0

    used = extract_skip_markers(out)
    registered = registry_markers()
    print("=== 豁免使用审计（git 历史） ===")
    print(f"历史中出现的豁免标记: {sorted(used) if used else '（无）'}")
    print(f"清单已登记标记:       {sorted(registered) if registered else '（无）'}")
    unregistered = used - registered
    if unregistered:
        print(f"⚠ 用过但未登记的标记: {sorted(unregistered)}")
    else:
        print("✓ 所有历史使用的豁免标记均已登记")
    return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--audit":
        return audit()

    if len(sys.argv) != 2:
        print(
            "用法: python check_exemption_log.py <commit_msg_file> | --audit",
            file=sys.stderr,
        )
        return 1

    msg_file = Path(sys.argv[1])
    if not msg_file.exists():
        print(f"FAIL: commit-msg 文件不存在: {msg_file}", file=sys.stderr)
        return 1

    msg = msg_file.read_text(encoding="utf-8")
    markers = extract_skip_markers(msg)

    # 1. 无豁免标记 → 放行（零摩擦）
    if not markers:
        return 0

    # 2a. 每个标记必须在清单已登记
    registered = registry_markers()
    unregistered = markers - registered
    if unregistered:
        print(
            f"FAIL: 使用了未登记的豁免标记 {sorted(unregistered)}",
            file=sys.stderr,
        )
        shown = sorted(registered) if registered else "（无 / 清单不存在）"
        print(f"  已登记标记: {shown}", file=sys.stderr)
        print(
            f"  修复: 在 {REGISTRY_REL} §二「已登记豁免标记」先登记该标记",
            file=sys.stderr,
        )
        return 1

    # 2b. 本次提交必须同时修改清单（追加使用记录）
    if REGISTRY_REL not in staged_files():
        print(
            f"FAIL: commit message 含豁免标记 {sorted(markers)}，但本次提交未修改 {REGISTRY_REL}",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(f"  每次用豁免必须登记：{REGISTRY_REL} §三 追加一行", file=sys.stderr)
        print(f"  然后 `git add {REGISTRY_REL}` 一起提交", file=sys.stderr)
        return 1

    print(f"OK 豁免已登记: {sorted(markers)}（清单已 staged）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
