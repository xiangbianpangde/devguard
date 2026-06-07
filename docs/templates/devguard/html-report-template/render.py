#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render.py — html-report-template 渲染脚本
=============================================
占位替换用 string.Template（$name 语法），不和 CSS 的 { } 冲突。

用法:
    python render.py --meta /path/to/_meta.yaml --status /path/to/STATUS.md --out /path/to/index.html

新项目 fork 流程:
    1. 复制 docs/templates/devguard/html-report-template/ 到新项目
    2. python render.py --meta ../conventions/_meta.yaml --status ../STATUS.md --out ../dashboard.html
"""  # noqa: E501

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml
from string import Template

TEMPLATE_FILE = Path(__file__).resolve().parent / "index.html"


def load_meta(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_status(path: Path) -> list[dict]:
    """解析 STATUS.md '## 当前进度' 节内表格（只取第一个表格，忽略 '## 收束节点历史' 等其他节）

    边界条件：STATUS.md 可能含多个 markdown 表格（当前进度 + 收束历史 + 阻塞项等），
    此函数只取 '## 当前进度' 节后的第一个表格。
    """
    if not path.exists():
        return []
    rows: list[dict] = []
    in_progress_section = False
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        # 跟踪是否在 ## 当前进度 节内
        if line.startswith("## "):
            in_progress_section = "当前进度" in line
            in_table = False  # 进入新节就重置表格状态
            continue
        if not in_progress_section:
            continue
        # 进入表格：检测 |--- 分隔符（前面是表头行）
        if not in_table:
            if "---" in line and "|" in line:
                in_table = True
            continue
        # 已进入表格
        if not line.strip().startswith("|"):
            in_table = False
            continue
        # 跳过表头：精确匹配第一列 == "功能点"（BDD 列含"BDD" 字符串的合法数据行不跳）
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols and cols[0] == "功能点":
            continue
        if len(cols) >= 4:
            rows.append(
                {
                    "num": cols[0],
                    "name": cols[1] if len(cols) > 1 else "",
                    "status": cols[2] if len(cols) > 2 else "",
                    "bdd": cols[3] if len(cols) > 3 else "",
                    "date": cols[4] if len(cols) > 4 else "",
                }
            )
    return rows


def render_convention_rows(meta: dict) -> str:
    """渲染规范表行"""
    rows: list[str] = []
    for conv in meta.get("conventions", []):
        cid = conv.get("id", "?")
        title = conv.get("title", "")
        grade = conv.get("grade", {})
        l1 = conv.get("l1_check", "")
        l3 = conv.get("l3_route", "")
        rows.append(
            f"<tr><td><code>{cid}</code> {title}</td>"
            f"<td>{grade.get('red_line', 0)}</td>"
            f"<td>{grade.get('warning', 0)}</td>"
            f"<td>{grade.get('recommend', 0)}</td>"
            f"<td><code>{l1}</code></td>"
            f"<td>{l3}</td></tr>"
        )
    return "\n      ".join(rows)


def render_status_rows(rows: list[dict]) -> str:
    """渲染 STATUS.md 表格行"""
    if not rows:
        return '<tr><td colspan="5">无 STATUS.md 数据</td></tr>'
    out: list[str] = []
    for r in rows:
        status = r["status"]
        if "完成" in status:
            cls = "ok"
        elif "WIP" in status or "失败" in status:
            cls = "warn"
        else:
            cls = ""
        out.append(
            f"<tr><td>{r['num']}</td><td>{r['name']}</td>"
            f"<td class=\"{cls}\">{status}</td><td>{r['bdd']}</td><td>{r['date']}</td></tr>"
        )
    return "\n      ".join(out)


def compute_progress(status_rows: list[dict]) -> tuple[int, int, int]:
    total = len(status_rows)
    done = sum(1 for r in status_rows if "完成" in r["status"])
    pct = int(done / total * 100) if total > 0 else 0
    return done, total, pct


def render(
    meta_path: Path, status_path: Path, out_path: Path, l4_passed: int, l4_total: int
) -> None:
    meta = load_meta(meta_path)
    status_rows = parse_status(status_path)
    done, total, pct = compute_progress(status_rows)
    red_line_total = sum(
        c.get("grade", {}).get("red_line", 0) for c in meta.get("conventions", [])
    )
    template_text = TEMPLATE_FILE.read_text(encoding="utf-8")
    template = Template(template_text)
    # V3.3 幂等性修复：render_date 用 git HEAD commit time（同 commit 多次 render 输出相同）
    # 不用 datetime.now()——否则 CI 每次跑都 drift，drift check 必 fail
    try:
        # git 是固定 binary，args 来自 _meta.yaml/STATUS.md（仓库内文件）受信任
        result = subprocess.run(  # noqa: S603, S607
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=out_path.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_time = result.stdout.strip()  # git SHA short (7 字符)
    except Exception:
        commit_time = "unknown"
    output = template.safe_substitute(
        project_name=meta.get("project", "Unknown"),
        render_date=commit_time,
        progress_done=done,
        progress_total=total,
        progress_pct=pct,
        convention_count=len(meta.get("conventions", [])),
        red_line_total=red_line_total,
        l4_passed=l4_passed,
        l4_total=l4_total,
        convention_rows=render_convention_rows(meta),
        status_rows=render_status_rows(status_rows),
    )
    out_path.write_text(output, encoding="utf-8")
    print(f"OK 渲染 → {out_path}（{total} 功能点，{pct}% 完成，{red_line_total} 红线）")


def main() -> int:
    parser = argparse.ArgumentParser(description="渲染 html-report-template")
    parser.add_argument("--meta", required=True, help="conventions/_meta.yaml 路径")
    parser.add_argument("--status", required=True, help="STATUS.md 路径")
    parser.add_argument("--out", required=True, help="输出 HTML 路径")
    parser.add_argument("--l4-passed", type=int, default=0, help="L4 规范测试通过数")
    parser.add_argument("--l4-total", type=int, default=0, help="L4 规范测试总数")
    args = parser.parse_args()
    render(
        Path(args.meta),
        Path(args.status),
        Path(args.out),
        args.l4_passed,
        args.l4_total,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
