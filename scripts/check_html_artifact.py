#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_html_artifact.py — commit-msg 钩子：HTML 产出物章节/结构校验（V2.3 #48）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段D
"产出物格式无强制" → 为 HTML 模板族产出物建章节/结构级 L1（对标 #40-#42，
用结构而非逐字）。

模板族与结构契约（docs/templates/*.html，头部 <meta name="doc-template"> 声明类型）：
  report        汇报模板      ：04-长程开发 §五 验收报告 8 要素（7 个章节锚点）
  plan          计划模板      ：五段式设计提案（背景/目标/方案/影响/风险）+ Owner 决策
  impl-design   实施设计模板  ：03-设计规范 §四 实现计划 8 节（5 个结构块锚点）
  asset-library 绘图素材库    ：图型 / 组件 / 样式令牌 / 使用说明

判定逻辑（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. commit message 含 [skip-html] → 放行（豁免须登记 meta/豁免清单.md）
  2. 取本次 staged 的受查 .html（docs/reports/ + docs/plan/design/ + docs/templates/）
  3. 带类型声明（meta doc-template）的文件 → 按类型契约硬校验：
     DOCTYPE / <title> / <nav 锚点导航 / 全部必备 <section id="..."> → 缺任一 FAIL
  4. 未带类型声明的产出物（legacy / 非模板族）→ 仅 WARN 提示采用模板族，不拦
     （分粒度原则：声明了契约的硬拦，存量的先软提示——见设计 §1.4）

附加用法：
  python scripts/check_html_artifact.py --all   # 全仓受查 html 审计（CI 用），typed 违规 exit 1

用法（pre-commit 框架调用）:
    python scripts/check_html_artifact.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_MARKER = "[skip-html]"

# 受查范围：HTML 产出物落点 + 模板族自身
SCOPE_PREFIXES = ("docs/reports/", "docs/plan/design/", "docs/templates/")

META_TYPE = re.compile(r'<meta\s+name="doc-template"\s+content="([\w-]+)"', re.IGNORECASE)
SECTION_ID = re.compile(r'<section\s+[^>]*id="([\w-]+)"', re.IGNORECASE)

# 类型 → 必备章节锚点（结构契约，校验存在性而非逐字）
TYPE_CONTRACTS: dict[str, list[str]] = {
    # 04-长程开发 §五 验收报告 8 要素（要素3"可视化/高密度"为全局性质，不设锚点）
    "report": [
        "sec-evidence",
        "sec-code",
        "sec-tasks",
        "sec-design",
        "sec-commits",
        "sec-status",
        "sec-handoff",
    ],
    # 五段式设计提案 + Owner 决策（开工前须清零待拍板）
    "plan": [
        "sec-background",
        "sec-goals",
        "sec-plan",
        "sec-impact",
        "sec-risks",
        "sec-decisions",
    ],
    # 03-设计规范 §四 实现计划 8 节（总览/阶段路径/里程碑/测试/红线 5 个结构块）
    "impl-design": [
        "sec-overview",
        "sec-stages",
        "sec-milestones",
        "sec-testing",
        "sec-redlines",
    ],
    # 绘图素材库：图型/组件/样式令牌/用法
    "asset-library": [
        "sec-mermaid",
        "sec-components",
        "sec-styles",
        "sec-usage",
    ],
}


def in_scope(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    return rel.endswith(".html") and rel.startswith(SCOPE_PREFIXES)


def check_content(rel: str, content: str) -> tuple[list[str], list[str]]:
    """校验单个 HTML 产出物，返回 (errors, warnings)。"""
    errors: list[str] = []
    warnings: list[str] = []

    m = META_TYPE.search(content)
    if m is None:
        # 模板目录里未声明类型的 html（dashboard 渲染模板等）不打扰；
        # 产出物目录（reports / plan/design）未声明 → 软提示采用模板族
        if not rel.startswith("docs/templates/"):
            warnings.append(
                f"{rel}: 未声明 doc-template 类型（建议从 docs/templates/ "
                f'HTML 模板族复制，携带 <meta name="doc-template">）'
            )
        return errors, warnings

    doc_type = m.group(1)
    contract = TYPE_CONTRACTS.get(doc_type)
    if contract is None:
        errors.append(
            f"{rel}: doc-template 类型「{doc_type}」未知"
            f"（合法：{'/'.join(sorted(TYPE_CONTRACTS))}）"
        )
        return errors, warnings

    if "<!DOCTYPE html" not in content and "<!doctype html" not in content:
        errors.append(f"{rel}: 缺 <!DOCTYPE html>")
    if "<title>" not in content.lower():
        errors.append(f"{rel}: 缺 <title>")
    if "<nav" not in content.lower():
        errors.append(f"{rel}: 缺 <nav> 锚点导航（03-设计规范 §八 HTML 渲染规范）")

    present = set(SECTION_ID.findall(content))
    missing = [s for s in contract if s not in present]
    if missing:
        errors.append(f"{rel}: 类型 {doc_type} 缺必备章节 {missing}")

    return errors, warnings


def staged_in_scope() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    staged = {ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()}
    return sorted(f for f in staged if in_scope(f))


def staged_content(path: str) -> str:
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


def audit_all() -> int:
    """全仓受查 html 审计（CI 用）：typed 违规 exit 1，untyped 仅汇总。"""
    errors: list[str] = []
    warnings: list[str] = []
    n = 0
    for prefix in SCOPE_PREFIXES:
        base = REPO_ROOT / prefix
        if not base.exists():
            continue
        for fp in sorted(base.rglob("*.html")):
            rel = fp.relative_to(REPO_ROOT).as_posix()
            n += 1
            errs, warns = check_content(rel, fp.read_text(encoding="utf-8"))
            errors.extend(errs)
            warnings.extend(warns)
    for w in warnings:
        print(f"WARN {w}")
    if errors:
        print(f"FAIL HTML 产出物审计（{n} 个受查）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK HTML 产出物审计通过（{n} 个受查，untyped 提示 {len(warnings)} 条）")
    return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--all":
        return audit_all()

    if len(sys.argv) != 2:
        print(
            "用法: python check_html_artifact.py <commit_msg_file> | --all",
            file=sys.stderr,
        )
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-html]，跳过 HTML 结构校验")
        return 0

    files = staged_in_scope()
    if not files:
        return 0

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for path in files:
        errs, warns = check_content(path, staged_content(path))
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for w in all_warnings:
        print(f"WARN {w}")

    if all_errors:
        print("FAIL HTML 产出物结构校验不通过：", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  契约: docs/templates/ HTML 模板族（汇报8要素/计划五段/实施设计8节/素材库4区）",
            file=sys.stderr,
        )
        print("  豁免: 末尾加 [skip-html]（须登记 meta/豁免清单.md）", file=sys.stderr)
        return 1

    print(f"OK HTML 结构校验通过（{len(files)} 个受查文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
