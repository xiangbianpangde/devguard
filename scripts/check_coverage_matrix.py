#!/usr/bin/env python3
"""约束覆盖率矩阵机器校验（2026-08-13 R-10：矩阵 ↔ _meta.yaml 真源逐行核对）。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Windows 中文 stdout 兼容（cp1252 下打印中文会 UnicodeEncodeError）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import yaml

MATRIX_REL = "meta/约束覆盖率矩阵.md"
META_REL = "conventions/_meta.yaml"


def default_repo_root() -> Path:
    import os

    configured = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def parse_matrix_rows(text: str) -> dict[str, list[str]]:
    """Parse §二 table rows: id → [L1 检测, 钩子拦截, CI 拦截, 人工检查]."""
    section = text.split("## 二、17 规范 × 强制方式", 1)
    if len(section) < 2:
        return {}
    rows: dict[str, list[str]] = {}
    for line in section[1].splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in {"#", "规范"}:
            continue
        match = re.match(r"^(\d{2})$", cells[0])
        if not match:
            continue
        rows[match.group(1)] = cells[1:]
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()

    matrix_path = root / MATRIX_REL
    meta_path = root / META_REL
    if not matrix_path.is_file():
        print(f"FAIL 矩阵缺失: {MATRIX_REL}", file=sys.stderr)
        return 1
    if not meta_path.is_file():
        print(f"FAIL 真源缺失: {META_REL}", file=sys.stderr)
        return 1

    matrix = parse_matrix_rows(matrix_path.read_text(encoding="utf-8"))
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    conventions = meta.get("conventions", [])

    errors: list[str] = []
    meta_ids = {str(item.get("id")).split("-")[0] for item in conventions}
    if len(meta_ids) != 17:
        errors.append(f"_meta.yaml 规范数 {len(meta_ids)} != 17")

    # 1. 集合一致性：矩阵行 ↔ _meta.yaml 规范
    missing_in_matrix = sorted(meta_ids - set(matrix))
    extra_in_matrix = sorted(set(matrix) - meta_ids)
    if missing_in_matrix:
        errors.append(f"矩阵缺规范行: {missing_in_matrix}")
    if extra_in_matrix:
        errors.append(f"矩阵含 _meta.yaml 之外的规范行: {extra_in_matrix}")

    # 2. L1 检测工具映射：_meta.yaml l1_check 的工具关键词必须出现在矩阵 L1 列
    tool_words = {
        "01": "importlinter",
        "02": "ruff",
        "03": "pre-commit",
        "04": "spectral",
        "05": "pytest",
        "06": "markdownlint",
        "07": "一致性",
        "08": "check_code_understanding",
        "09": "render_meta",
        "10": "模板",
        "11": "README",
        "12": "CODEOWNERS",
        "13": "CHANGELOG",
        "14": "SECURITY",
        "15": "SUPPORT",
        "16": "LICENSE",
        "17": "CONTRIBUTING",
    }
    for item in conventions:
        cid = str(item.get("id")).split("-")[0]
        row = matrix.get(cid)
        if row is None:
            continue
        l1_cell = row[1]  # row[0]=规范名, row[1]=L1 检测列
        if cid == "07":
            # 07 特殊：一致性矩阵 + 故障注入两词都在
            if "一致性" not in l1_cell or "故障注入" not in l1_cell:
                errors.append(f"矩阵 07 L1 列缺「一致性/故障注入」: {l1_cell[:40]}")
            continue
        keyword = tool_words.get(cid, "")
        if not keyword:
            continue
        if cid in {"11", "12", "13", "14", "15", "16", "17"}:
            # 文件存在型规范：L1 列统一为「文件存在（章节级 L1）」，关键词检查任意列
            haystack = " | ".join(row).lower()
            if keyword.lower() not in haystack:
                errors.append(f"矩阵 {cid} 行缺规范名「{keyword}」")
            continue
        if keyword.lower() not in l1_cell.lower():
            errors.append(f"矩阵 {cid} L1 列缺工具关键词「{keyword}」: {l1_cell[:40]}")

    if errors:
        print("FAIL 约束覆盖率矩阵与真源不一致：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"OK 约束覆盖率矩阵校验通过（{len(matrix)}/{len(meta_ids)} 规范逐行一致）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
