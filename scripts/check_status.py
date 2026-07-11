#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_status.py — STATUS.md 章节级 L1 钩子（V2.1 #40）
============================================================
对标 check_ai_workflow.py：把"入口文件结构完整性"从人工检查升级为工具验证。
依据：流程强制化方案 #40 + 09-dashboard-gen（STATUS.md 是 dashboard 数据源）

校验项：
  a. `## 当前进度` 节存在
  b. 该节第一张表格列数 ≥ 4
  c. 该表「状态」列每行取值含合法符号之一 {✅,🔄,⏳,🚫}
  d. `## 收束节点历史` 节存在且其表格列数 ≥ 9

退出码: 0 = 通过；1 = 不通过（CI l4-conventions 阶段拦截）

用法:
    python scripts/check_status.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_FILE = REPO_ROOT / "STATUS.md"

LEGAL_STATUS = {"✅", "🔄", "⏳", "🚫"}


def split_row(line: str) -> list[str]:
    """拆一行 markdown 表格为单元格列表（去首尾 | 与空白）"""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def first_table_after(lines: list[str], heading_kw: str) -> list[list[str]]:
    """返回某 `## ` 标题节内第一张表格的所有数据行（不含表头与分隔行）。

    找不到节或表格则返回空列表。表头行单独由 table_header_after 取。
    """
    rows, header = _table_after(lines, heading_kw)
    return rows


def _table_after(lines: list[str], heading_kw: str) -> tuple[list[list[str]], list[str]]:
    in_section = False
    in_table = False
    seen_sep = False
    header: list[str] = []
    rows: list[list[str]] = []
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break  # 离开目标节
            in_section = heading_kw in line
            in_table = False
            seen_sep = False
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not in_table:
            if stripped.startswith("|"):
                header = split_row(line)
                in_table = True
            continue
        # 已在表格区
        if not stripped.startswith("|"):
            if seen_sep:
                break  # 表格结束
            continue
        if "---" in stripped and not seen_sep:
            seen_sep = True
            continue
        rows.append(split_row(line))
    return rows, header


def table_header_after(lines: list[str], heading_kw: str) -> list[str]:
    _, header = _table_after(lines, heading_kw)
    return header


def main() -> int:
    if not STATUS_FILE.exists():
        print("FAIL: STATUS.md 不存在", file=sys.stderr)
        return 1

    lines = STATUS_FILE.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []

    # a. ## 当前进度 节存在
    progress_header = table_header_after(lines, "当前进度")
    progress_rows = first_table_after(lines, "当前进度")
    if not progress_header:
        errors.append("缺 `## 当前进度` 节或该节无表格")
    else:
        # b. 列数 ≥ 4
        if len(progress_header) < 4:
            errors.append(f"`## 当前进度` 表列数 {len(progress_header)} < 4（{progress_header}）")
        # c. 状态列合法
        # 状态列：表头里含「状态」的列，取不到则默认第 3 列（index 2）
        status_idx = next((i for i, h in enumerate(progress_header) if "状态" in h), 2)
        for r in progress_rows:
            if status_idx >= len(r):
                continue
            cell = r[status_idx]
            if not any(sym in cell for sym in LEGAL_STATUS):
                errors.append(
                    f"`## 当前进度` 状态列非法值「{cell}」（合法: {sorted(LEGAL_STATUS)}）"
                )

    # d. ## 收束节点历史 表列数 ≥ 9
    conv_header = table_header_after(lines, "收束节点历史")
    if not conv_header:
        errors.append("缺 `## 收束节点历史` 节或该节无表格")
    elif len(conv_header) < 9:
        errors.append(f"`## 收束节点历史` 表列数 {len(conv_header)} < 9（{conv_header}）")

    if errors:
        print("FAIL STATUS.md 章节级 L1 验证不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK STATUS.md 章节级 L1 验证通过"
        f"（当前进度 {len(progress_header)} 列 / {len(progress_rows)} 行，"
        f"收束节点历史 {len(conv_header)} 列）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
