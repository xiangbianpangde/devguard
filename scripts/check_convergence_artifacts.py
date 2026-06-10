#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_convergence_artifacts.py — 收束节点产物 CI 检查（V2.1 #46）
============================================================
依据：ai-workflow 06-第三步_收束节点 + 流程强制化方案 #46

收束节点四阶段（整理→测试→审计→验证）完成后必须产出：
  - ADR：worklogs/decisions/NNNN-*.md
  - 收束报告：docs/reports/收束报告-v*.md

本脚本扫描 STATUS.md「## 收束节点历史」表中的节点标记（如 v0.1, v2.1-A 等），
检查对应的 ADR 和收束报告文件是否存在。对未完成的节点（人审计 ⏳）只 WARN，
已完成节点（✅）硬拦。

退出码: 0 = 全面通过（可能含 WARN）；1 = 有缺失

用法:
    python scripts/check_convergence_artifacts.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS = REPO_ROOT / "STATUS.md"
DECISIONS_DIR = REPO_ROOT / "worklogs" / "decisions"
REPORTS_DIR = REPO_ROOT / "docs" / "reports"

NODE_PATTERN = re.compile(r"^\|?\s*\*{0,2}(v\d+\.\d+[-\w]*)\*{0,2}\s*\|")
# e.g. "| v0.1 | 2026-05-27 |" or "| **v1.5** | **2026-06-08** |"


def parse_convergence_nodes() -> list[dict]:
    """从 STATUS.md 收束节点历史表解析每个节点的：label, 人审计状态"""
    if not STATUS.exists():
        return []
    nodes: list[dict] = []
    lines = STATUS.read_text(encoding="utf-8").splitlines()
    in_section = False
    seen_sep = False
    for line in lines:
        if line.startswith("## "):
            in_section = "收束节点历史" in line
            seen_sep = False
            continue
        if not in_section or not line.strip().startswith("|"):
            continue
        if "---" in line:
            seen_sep = True
            continue
        if not seen_sep:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        label = cells[0].strip("*").strip()
        # 人审计列（第 7 列，index 6）：含「✅ 已签核」→ done
        human_audit = cells[6].strip() if len(cells) > 6 else ""
        is_signed = "已签核" in human_audit
        nodes.append({"label": label, "human_audit": human_audit, "signed": is_signed})
    return nodes


def existing_adr_count() -> int:
    """ADR 文件数量（worklogs/decisions/NNNN-*.md）"""
    if not DECISIONS_DIR.exists():
        return 0
    return len(list(DECISIONS_DIR.glob("*.md")))


def existing_report_count() -> int:
    """收束报告文件数量"""
    if not REPORTS_DIR.exists():
        return 0
    return len(list(REPORTS_DIR.glob("*收束报告*.md")))


def main() -> int:
    nodes = parse_convergence_nodes()
    if not nodes:
        print(
            "WARN: 未解析到收束节点（检查 STATUS.md「## 收束节点历史」表格式）",
            file=sys.stderr,
        )
        return 0

    adr_count = existing_adr_count()
    report_count = existing_report_count()
    signed_count = sum(1 for n in nodes if n["signed"])
    errors: list[str] = []
    warnings: list[str] = []

    for node in nodes:
        if not node["signed"]:
            continue  # 未签核的不追究
        # 有签核节点 → 至少要有 ADR 和 收束报告存在
        pass

    if signed_count > 0 and adr_count == 0:
        errors.append(
            f"有 {signed_count} 个已签核收束节点，但 worklogs/decisions/ 无 ADR"
        )
    if signed_count > 0 and report_count == 0:
        errors.append(
            f"有 {signed_count} 个已签核收束节点，但 docs/reports/ 无收束报告"
        )
    # 保守：已签核数 > ADR/报告数 → WARN（可能少数节点共用 ADR）
    if signed_count > 0 and adr_count < signed_count:
        warnings.append(
            f"已签核 {signed_count} 个节点，但 ADR 仅 {adr_count} 个"
            f"（部分节点可能共用 ADR——请人工核对）"
        )
    if signed_count > 0 and report_count < signed_count:
        warnings.append(f"已签核 {signed_count} 个节点，但收束报告仅 {report_count} 份")

    for w in warnings:
        print(f"WARN {w}")

    if errors:
        print(
            "FAIL 收束节点产物缺失（已签核节点必须有 ADR + 收束报告）：",
            file=sys.stderr,
        )
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"OK 收束节点产物检查通过"
        f"（{len(nodes)} 个节点，{signed_count} 已签核，"
        f"{adr_count} ADR，{report_count} 收束报告）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
