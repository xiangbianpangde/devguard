#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_plan.py — 开发清单.md 格式 L1 + 交叉校验钩子（V2.1 #42）
============================================================
依据：流程强制化方案 #42 + 10-templates-reporting

校验项：
  a. `## 功能点列表` 节存在且有表格（硬拦）
  b. 该表列数 ≥ 7（#/功能点/BDD规格/状态/预估轮次/依赖/完成日期）（硬拦）
  c. 所有功能点行（首列为整数）含合法状态符号 {✅,🔄,⏳,🚫}（硬拦）
  d. 开发清单功能点总数 与 STATUS.md 详细功能点列表行数一致（软提示 / WARN）
     —— 方案"风险"章节要求跨文件一致性先豁免历史差异、只警告不拦截。

退出码: 0 = 结构通过（可能含 WARN）；1 = 结构不通过

用法:
    python scripts/check_plan.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_FILE = REPO_ROOT / "docs" / "plan" / "开发清单.md"
STATUS_FILE = REPO_ROOT / "STATUS.md"

LEGAL_STATUS = {"✅", "🔄", "⏳", "🚫"}
INT_CELL = re.compile(r"^\*{0,2}\d+\*{0,2}$")  # 1 / 22 / **36**


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_table_row(line: str) -> bool:
    return line.strip().startswith("|")


def functional_point_rows(lines: list[str]) -> list[list[str]]:
    """全文里所有"功能点行"：表格行且首列是整数（允许 **加粗**）。"""
    out: list[list[str]] = []
    for line in lines:
        if not is_table_row(line):
            continue
        cells = split_row(line)
        if cells and INT_CELL.match(cells[0]):
            out.append(cells)
    return out


def header_after(lines: list[str], heading_kw: str) -> list[str]:
    """某 `## ` 节内第一张表格的表头行单元格。"""
    in_section = False
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            in_section = heading_kw in line
            continue
        if in_section and is_table_row(line):
            return split_row(line)
    return []


def status_detail_row_count() -> int | None:
    """STATUS.md『详细功能点列表』节的数据行数（功能点行）。"""
    if not STATUS_FILE.exists():
        return None
    lines = STATUS_FILE.read_text(encoding="utf-8").splitlines()
    in_section = False
    seen_sep = False
    count = 0
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            in_section = "详细功能点列表" in line
            seen_sep = False
            continue
        if not in_section or not is_table_row(line):
            continue
        s = line.strip()
        if "---" in s and not seen_sep:
            seen_sep = True
            continue
        if seen_sep:
            # 跳过表头行（首列 == 功能点）
            cells = split_row(line)
            if cells and cells[0] != "功能点":
                count += 1
    return count


def main() -> int:
    if not PLAN_FILE.exists():
        print("FAIL: docs/plan/开发清单.md 不存在", file=sys.stderr)
        return 1

    lines = PLAN_FILE.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    warnings: list[str] = []

    # a + b
    header = header_after(lines, "功能点列表")
    if not header:
        errors.append("缺 `## 功能点列表` 节或该节无表格")
    elif len(header) < 7:
        errors.append(f"`## 功能点列表` 表列数 {len(header)} < 7（{header}）")

    # c. 功能点行状态合法
    fp_rows = functional_point_rows(lines)
    if not fp_rows:
        errors.append("未找到任何功能点行（首列为整数的表格行）")
    for r in fp_rows:
        if not any(sym in cell for cell in r for sym in LEGAL_STATUS):
            errors.append(
                f"功能点行 #{r[0]} 缺合法状态符号 {sorted(LEGAL_STATUS)}：{r[:4]}"
            )

    # d. 与 STATUS.md 交叉计数（WARN）
    plan_count = len(fp_rows)
    status_count = status_detail_row_count()
    if status_count is None:
        warnings.append("STATUS.md 不存在，跳过交叉计数")
    elif plan_count != status_count:
        warnings.append(
            f"开发清单功能点数({plan_count}) ≠ STATUS 详细列表行数({status_count})"
            f"——历史差异请人工核对（方案风险章节：跨文件不一致先警告不拦截）"
        )

    for w in warnings:
        print(f"WARN {w}")

    if errors:
        print("FAIL 开发清单.md 格式 L1 验证不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK 开发清单.md 格式 L1 验证通过"
        f"（功能点列表 {len(header)} 列，{plan_count} 个功能点行）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
