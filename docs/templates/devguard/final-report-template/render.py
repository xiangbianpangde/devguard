"""
final-report-template/render.py
================================
把 template.html 里的具体数据替换为占位符（首次生成），并演示如何用占位符生成报告。

模板设计：
- 模板中保留 8 大类占位符（双花括号风格）
- render.py 接收 --data 参数（JSON 文件）做替换
- 不依赖 Jinja2，纯 stdlib 即可
"""

import re  # noqa: F401  (预留, 未来扩展可用)
import sys
import json
import argparse
from pathlib import Path

TEMPLATE = Path(__file__).parent / "template.html"

# === 占位符清单（与 README.md 对齐） ===
PLACEHOLDERS = [
    # 基础
    ("{{PROJECT_NAME}}", "项目名（用于 brand、title）"),
    ("{{REPORT_TITLE}}", "报告主标题"),
    ("{{REPORT_SUBTITLE}}", "副标题/摘要"),
    ("{{REPORT_DATE}}", "报告日期"),
    # 周期 & 状态
    ("{{PERIOD_START}}", "项目起始日期"),
    ("{{PERIOD_END}}", "项目结束日期"),
    ("{{GIT_BRANCH}}", "当前 git 分支"),
    ("{{WORKSPACE_STATUS}}", "工作区状态：clean/dirty"),
    # KPI 数字（8 个）
    ("{{KPI_1_NUM}}", "KPI1 数字（默认 17）"),
    ("{{KPI_1_LBL}}", "KPI1 标签（默认 '规范文档'）"),
    ("{{KPI_1_SUB}}", "KPI1 描述"),
    ("{{KPI_2_NUM}}", "KPI2 数字（默认 65）"),
    ("{{KPI_2_LBL}}", "KPI2 标签"),
    ("{{KPI_2_SUB}}", "KPI2 描述"),
    ("{{KPI_3_NUM}}", "KPI3 数字（默认 10）"),
    ("{{KPI_3_LBL}}", "KPI3 标签"),
    ("{{KPI_3_SUB}}", "KPI3 描述"),
    ("{{KPI_4_NUM}}", "KPI4 数字（默认 5）"),
    ("{{KPI_4_LBL}}", "KPI4 标签"),
    ("{{KPI_4_SUB}}", "KPI4 描述"),
    ("{{KPI_5_NUM}}", "KPI5 数字（默认 13）"),
    ("{{KPI_5_LBL}}", "KPI5 标签"),
    ("{{KPI_5_SUB}}", "KPI5 描述"),
    ("{{KPI_6_NUM}}", "KPI6 数字（默认 6）"),
    ("{{KPI_6_LBL}}", "KPI6 标签"),
    ("{{KPI_6_SUB}}", "KPI6 描述"),
    ("{{KPI_7_NUM}}", "KPI7 数字（默认 50）"),
    ("{{KPI_7_LBL}}", "KPI7 标签"),
    ("{{KPI_7_SUB}}", "KPI7 描述"),
    ("{{KPI_8_NUM}}", "KPI8 数字（默认 6）"),
    ("{{KPI_8_LBL}}", "KPI8 标签"),
    ("{{KPI_8_SUB}}", "KPI8 描述"),
    # 5 维健康度（百分比）
    ("{{HEALTH_DIM_1}}", "健康度维度1 名"),
    ("{{HEALTH_DIM_1_PCT}}", "健康度维度1 百分比"),
    ("{{HEALTH_DIM_2}}", "健康度维度2 名"),
    ("{{HEALTH_DIM_2_PCT}}", "健康度维度2 百分比"),
    ("{{HEALTH_DIM_3}}", "健康度维度3 名"),
    ("{{HEALTH_DIM_3_PCT}}", "健康度维度3 百分比"),
    ("{{HEALTH_DIM_4}}", "健康度维度4 名"),
    ("{{HEALTH_DIM_4_PCT}}", "健康度维度4 百分比"),
    ("{{HEALTH_DIM_5}}", "健康度维度5 名"),
    ("{{HEALTH_DIM_5_PCT}}", "健康度维度5 百分比"),
]


def apply_data(template_text: str, data: dict) -> str:
    """把 {{占位}} 替换为 data 里的值，未匹配的占位符保留并打 warning 注释。

    data 的 key 可以两种风格：
    - 不带花括号: "PROJECT_NAME" → 自动转 {{PROJECT_NAME}}
    - 带花括号:  "{{PROJECT_NAME}}" → 直接用
    """
    out = template_text
    missing = []
    for ph, _desc in PLACEHOLDERS:
        if ph not in out:
            continue
        # 查找 data 里的值（兼容两种 key 风格）
        key_no_braces = ph.strip("{}")
        value = None
        if ph in data:
            value = data[ph]
        elif key_no_braces in data:
            value = data[key_no_braces]
        if value is not None:
            out = out.replace(ph, str(value))
        else:
            missing.append(ph)
    if missing:
        print(f"[warn] {len(missing)} 个占位符未提供：{missing[:5]}...", file=sys.stderr)  # noqa: T201 (CLI 必要输出)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, help="JSON 数据文件（key=占位符名去花括号）")
    ap.add_argument("--out", type=Path, default=Path("report.html"), help="输出 HTML 路径")
    args = ap.parse_args()

    text = TEMPLATE.read_text(encoding="utf-8")
    if args.data and args.data.exists():
        data = json.loads(args.data.read_text(encoding="utf-8"))
        text = apply_data(text, data)

    args.out.write_text(text, encoding="utf-8")
    print(f"[ok] 报告已生成: {args.out} ({len(text):,} bytes)")  # noqa: T201 (CLI 必要输出)


if __name__ == "__main__":
    main()
