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
  d. 跨文件功能点口径一致：开发清单 与 STATUS.md 的 `<!-- fp -->` 标签数一致（软提示 / WARN）
     —— 口径统一方案：两边的「编号功能点」逐行打 `<!-- fp -->` 标签，本检查只数标签，
        不再拿"整数首列行 vs 全部数据行"两种口径硬比（那会因 STATUS 含 11 行 V0.6–V1.5
        衍展规范而恒不相等）。STATUS 详细列表里未打标的衍展行不计入功能点数。
        方案"风险"章节：跨文件不一致先警告不拦截。

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
FP_TAG = re.compile(r"<!--\s*fp\s*-->")  # 功能点统一计数标签


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


def fp_tag_count(path: Path) -> int | None:
    """文件中 `<!-- fp -->` 功能点标签的数量（统一口径计数）。"""
    if not path.exists():
        return None
    return len(FP_TAG.findall(path.read_text(encoding="utf-8")))


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
            errors.append(f"功能点行 #{r[0]} 缺合法状态符号 {sorted(LEGAL_STATUS)}：{r[:4]}")

    # d. 与 STATUS.md 跨文件口径一致：比 `<!-- fp -->` 标签数（WARN）
    plan_tags = fp_tag_count(PLAN_FILE)
    status_tags = fp_tag_count(STATUS_FILE)
    if status_tags is None:
        warnings.append("STATUS.md 不存在，跳过功能点标签交叉计数")
    elif plan_tags == 0:
        warnings.append("开发清单未发现 `<!-- fp -->` 功能点标签——口径统一方案要求逐功能点行打标")
    elif plan_tags != status_tags:
        warnings.append(
            f"功能点标签数不一致：开发清单({plan_tags}) ≠ STATUS 详细列表({status_tags})"
            f"——请确认两边「编号功能点」均已打 `<!-- fp -->`（衍展行不打标）"
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
        f"（功能点列表 {len(header)} 列，{len(fp_rows)} 个功能点行，"
        f"{plan_tags} 个 fp 标签 <-> STATUS {status_tags}）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
