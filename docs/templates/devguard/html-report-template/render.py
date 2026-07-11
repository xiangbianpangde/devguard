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
import os
import sys
from pathlib import Path

import yaml
from string import Template

TEMPLATE_FILE = Path(__file__).resolve().parent / "index.html"


def load_meta(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_section(path: Path, heading: str, *, detailed: bool) -> list[dict]:
    """Parse the first Markdown table under one named H2 section."""
    if not path.exists():
        return []
    rows: list[dict] = []
    in_section = False
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = heading in line
            in_table = False
            continue
        if not in_section:
            continue
        if not in_table:
            if "---" in line and "|" in line:
                in_table = True
            continue
        # 已进入表格
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols and cols[0] in {"#", "功能点", "阶段"}:
            continue
        if detailed and len(cols) >= 5:
            rows.append(
                {
                    "num": cols[0],
                    "name": cols[1],
                    "bdd": cols[2],
                    "status": cols[3],
                    "date": cols[4],
                }
            )
        elif not detailed and len(cols) >= 4:
            rows.append(
                {
                    "num": cols[0],
                    "name": cols[1],
                    "status": cols[2],
                    "bdd": "",
                    "date": cols[3],
                }
            )
    return rows


def parse_status(path: Path) -> list[dict]:
    """Parse numbered feature truth, with a legacy stage-table fallback."""
    detailed_rows = _parse_section(path, "详细功能点列表", detailed=True)
    return detailed_rows or _parse_section(path, "当前进度", detailed=False)


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
        if "✅" in status or "完成" in status:
            cls = "ok"
        elif "WIP" in status or "失败" in status:
            cls = "warn"
        else:
            cls = ""
        out.append(
            f"<tr><td>{r['num']}</td><td>{r['name']}</td>"
            f'<td class="{cls}">{status}</td><td>{r["bdd"]}</td><td>{r["date"]}</td></tr>'
        )
    return "\n      ".join(out)


def compute_progress(status_rows: list[dict]) -> tuple[int, int, int]:
    total = len(status_rows)
    done = sum(1 for r in status_rows if "✅" in r["status"] or "完成" in r["status"])
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
    # V3.3 幂等性修复：render_date 改为 static "latest"（不调 git，CI drift = 0）
    # 之前尝试用 git SHA / commit time，但每次新 commit HEAD 变，drift 必然
    # 用静态占位：dashboard.html 不因 render_date 字段变而需要重 commit
    commit_time = "latest"

    # V5.5: render mtime 自我刷新标识（用于 dashboard.html 自身识别是否新渲染）
    # 与 commit_time 不同：render_mtime 是 render 时的 mtime（不参与 drift check）
    # 但 render_mtime 也必须在 dashboard.html 落地 = 跟 commit_time 一样用环境变量传入
    render_mtime = os.environ.get("DASHBOARD_RENDER_MTIME", "build-time")
    output = template.safe_substitute(
        project_name=meta.get("project", "Unknown"),
        render_date=commit_time,
        render_mtime=render_mtime,
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
    # V3.3 跨平台 newline 一致性：强制写 LF（CI Linux 不转 CRLF）
    out_path.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK 渲染 → {out_path}（{total} 功能点，{pct}% 完成，{red_line_total} 红线）")


def main() -> int:
    parser = argparse.ArgumentParser(description="渲染 html-report-template")
    parser.add_argument("--meta", required=True, help="conventions/_meta.yaml 路径")
    parser.add_argument("--status", required=True, help="STATUS.md 路径")
    parser.add_argument("--out", required=True, help="输出 HTML 路径")

    # V7.2: 错误处理 - 接受空字符串/None 用 0 替代（V6.3 retry）
    def _to_int_or_zero(s: str) -> int:
        """V6.3 fix: argparse type=int 收空字符串会 ValueError；这里容忍"""
        if s is None or not str(s).strip():
            return 0
        return int(s)

    parser.add_argument(
        "--l4-passed", type=_to_int_or_zero, default=0, help="L4 规范测试通过数"
    )
    parser.add_argument(
        "--l4-total", type=_to_int_or_zero, default=0, help="L4 规范测试总数"
    )
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
