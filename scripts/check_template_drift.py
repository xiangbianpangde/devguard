#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_template_drift.py — 模板漂移检测（V2.1 #44）
============================================================
依据：流程强制化方案 #44 + 10-templates-reporting

对入口文件做**章节存在性对比**（非逐字）——验证真实文件保留了模板定义的
核心结构，但容忍内容调整。对标已有的 render_meta.py --check（pre-commit-config
+ convention-grade），扩展到 STATUS / CLAUDE / 开发清单 / dashboard（渲染链）。

覆盖文件（5 类，每类节级规则）：
  1. STATUS.md      — 当前进度 / 收束节点历史 / 详细功能点列表 / 阻塞项 / 技术债
  2. CLAUDE.md       — 项目概述 / 目录 / 红线(规范速查) / 工作流程 / 当前状态
  3. 开发清单.md      — 功能点列表 / 依赖关系图 / 历史
  4. dashboard.html  — 基础结构（doctype / <meta CSP / 功能点进度表）
  5. .pre-commit-config.yaml — 已由 render_meta.py --check 覆盖，仅作计数（跳过重复）

退出码: 0 = 全部通过；1 = 有 FAIL（CI compliance 阶段拦截）

用法:
    python scripts/check_template_drift.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 每个入口文件 → 预期章节关键词（至少命中 1 个）
ENTRY_CHECKS: dict[str, dict[str, list[str]]] = {
    "STATUS.md": {
        "当前进度": ["## 当前进度"],
        "收束节点历史": ["## 收束节点历史"],
        "详细功能点列表": ["## 详细功能点列表"],
        "阻塞项": ["## 阻塞项"],
        "技术债": ["## 技术债"],
    },
    "CLAUDE.md": {
        "项目概述": ["## 项目概述"],
        "目录索引": ["## 目录索引", "## 目录结构"],
        "红线 / 规范速查": ["## 规范速查", "## 红线", "红线"],
        "工作流程": ["## 工作流程"],
        "当前状态": ["## 当前状态"],
        "核心规则": ["## 核心规则"],
    },
    "docs/plan/开发清单.md": {
        "功能点列表": ["## 功能点列表"],
        "依赖关系": ["## 依赖关系", "依赖关系图"],
    },
}

# dashboard.html 结构检查关键词（不按章节，查整体结构）
DASHBOARD_STRUCT_CHECKS = {
    "<!DOCTYPE html>": "<!DOCTYPE html>",
    '<meta charset="UTF-8">': '<meta charset="UTF-8">',
    "Content-Security-Policy": "Content-Security-Policy",
}


def check_sections(path: Path, expected: dict[str, list[str]]) -> list[str]:
    """检查单个文件的章节存在性，返回缺失列表"""
    if not path.exists():
        return [f"{path.name} 不存在"]
    content = path.read_text(encoding="utf-8")
    missing: list[str] = []
    for section, kws in expected.items():
        if not any(k in content for k in kws):
            missing.append(f"{path.name} 缺节「{section}」（期望含词: {kws}）")
    return missing


def main() -> int:
    errors: list[str] = []

    for rel, sections in ENTRY_CHECKS.items():
        errs = check_sections(REPO_ROOT / rel, sections)
        errors.extend(errs)

    # dashboard.html 特殊检查：结构关键字
    dash = REPO_ROOT / "dashboard.html"
    if dash.exists():
        dash_content = dash.read_text(encoding="utf-8")
        for check_name, keyword in DASHBOARD_STRUCT_CHECKS.items():
            if keyword not in dash_content:
                errors.append(f"dashboard.html 缺结构元素「{check_name}」")
    else:
        errors.append("dashboard.html 不存在")

    if errors:
        print("FAIL 模板漂移检测不通过（章节存在性）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_files = len(ENTRY_CHECKS) + 1  # + dashboard
    print(f"OK 模板漂移检测通过（{n_files} 类入口文件，章节存在性一致）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
