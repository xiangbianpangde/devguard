#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_claude.py — CLAUDE.md 结构 L1 钩子（V2.1 #41）
============================================================
CLAUDE.md 是 AI 每会话自动加载的上下文，过时/缺段会让 AI 误判项目状态。
依据：流程强制化方案 #41

校验项：
  a. CLAUDE.md 存在
  b. 含必需章节（按概念同义匹配标题 / 正文）：
       项目概述 / 目录结构 / 红线表 / 工作流程 / 文件放置 / 当前状态
  c. 红线表（规范速查表）含 ≥ 6 个维度数据行

退出码: 0 = 通过；1 = 不通过

用法:
    python scripts/check_claude.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Windows 中文 stdout 兼容（cp1252 下打印中文会 UnicodeEncodeError）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_FILE = REPO_ROOT / "CLAUDE.md"

# 概念 -> 任一关键词命中（在标题行；文件放置/红线表也允许命中正文）
REQUIRED_IN_HEADINGS = {
    "项目概述": ["项目概述", "概述"],
    "目录结构": ["目录索引", "目录结构", "目录"],
    "红线表": ["红线", "规范速查"],
    "工作流程": ["工作流程", "流程"],
    "当前状态": ["当前状态", "状态"],
}
REQUIRED_IN_TEXT = {
    "文件放置": ["文件放置", "FILE_GRAPH"],
}


def _meta_l3_routes() -> dict[str, str]:
    """从 _meta.yaml 读取规范 id → l3_route 真源（R5-11）。"""
    meta_path = Path(__file__).resolve().parents[1] / "conventions" / "_meta.yaml"
    try:
        import yaml  # noqa: PLC0415

        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    routes: dict[str, str] = {}
    for conv in meta.get("conventions", []):
        cid = str(conv.get("id", "")).split("-")[0]
        route = conv.get("l3_route", "")
        if cid and route:
            routes[cid] = str(route)
    return routes


def main() -> int:
    if not CLAUDE_FILE.exists():
        print("FAIL: CLAUDE.md 不存在", file=sys.stderr)
        return 1

    content = CLAUDE_FILE.read_text(encoding="utf-8")
    lines = content.splitlines()
    headings = "\n".join(ln for ln in lines if ln.lstrip().startswith("#"))

    errors: list[str] = []

    for concept, kws in REQUIRED_IN_HEADINGS.items():
        if not any(k in headings for k in kws):
            errors.append(f"缺必需章节标题「{concept}」（期望标题含 {kws} 之一）")

    for concept, kws in REQUIRED_IN_TEXT.items():
        if not any(k in content for k in kws):
            errors.append(f"缺必需内容「{concept}」（期望正文含 {kws} 之一）")

    # c. 红线表 ≥ 6 维度行：找含「红线」且含「|」的表格段，数数据行
    redline_rows = _count_redline_table_rows(lines)
    if redline_rows < 6:
        errors.append(f"红线/规范速查表数据行 {redline_rows} < 6")

    # d. R5-11：AI 任务路由表与 _meta.yaml l3_route 真源一致（防路由静默漂移）
    routes = _meta_l3_routes()
    for cid, route in routes.items():
        keyword = "任务类型=" + route.split("任务类型=", 1)[-1].split("→")[0].strip()
        table_row = next(
            (ln for ln in lines if ln.lstrip().startswith("|") and f"| {cid} " in ln),
            None,
        )
        if table_row is None:
            # 速查表为精选版（01-06/08 常驻，07/09-17 不强制入表）——缺行仅提示不阻断
            print(f"NOTE: CLAUDE 速查表未列规范 {cid}（l3_route={route[:24]}…）")
            continue
        if keyword not in table_row:
            errors.append(f"CLAUDE 速查表 {cid} 行路由「{keyword}」与 _meta.yaml l3_route 不一致")

    if errors:
        print("FAIL CLAUDE.md 结构 L1 验证不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK CLAUDE.md 结构 L1 验证通过（红线表 {redline_rows} 行）")
    return 0


def _count_redline_table_rows(lines: list[str]) -> int:
    """定位『规范速查 / 红线』标题后的第一张表格，返回其数据行数。"""
    in_section = False
    in_table = False
    seen_sep = False
    count = 0
    for line in lines:
        if line.startswith("## "):
            if in_section and in_table:
                break
            in_section = ("红线" in line) or ("规范速查" in line)
            in_table = False
            seen_sep = False
            continue
        if not in_section:
            continue
        s = line.strip()
        if not in_table:
            if s.startswith("|"):
                in_table = True  # 表头行
            continue
        if not s.startswith("|"):
            if seen_sep:
                break
            continue
        if "---" in s and not seen_sep:
            seen_sep = True
            continue
        count += 1
    return count


if __name__ == "__main__":
    sys.exit(main())
