"""check_report.py — 收束报告结构 + 图表 L1 检测（汇报一致性强制）

检查 docs/reports/ 下 v2.0+ 收束报告：
- 必含章节：一、整理 / 二、测试 / 三、审计 / 四、效果验证 / 五、技术债
- 必含图表：≥1 mermaid 代码块 或 ≥2 表格（|---|）
- 必含收束结论

历史报告（v0.x/v1.x）豁免，保留原貌。
对应规范：07-ai-workflow §08-汇报收束 + 06-documentation §三配图规约
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / "docs" / "reports"

REQUIRED_SECTIONS = ["一、整理", "二、测试", "三、审计", "四、效果验证", "五、技术债"]


def version_key(name: str) -> tuple[int, ...]:
    m = re.search(r"v(\d+\.\d+)", name)
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0)


def check_report(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            errors.append(f"缺章节: {sec}")

    mermaid_count = text.count("```mermaid")
    table_count = text.count("|---|")
    if mermaid_count < 1 and table_count < 2:
        errors.append(
            f"图表不足: mermaid {mermaid_count}, 表格 {table_count}"
            "（需 ≥1 mermaid 或 ≥2 表格）"
        )

    if "收束结论" not in text:
        errors.append("缺收束结论")

    return errors


def main() -> int:
    reports = [
        p for p in REPORTS_DIR.glob("收束报告-v*.md") if version_key(p.name) >= (2, 0)
    ]
    if not reports:
        print("OK 无 v2.0+ 收束报告（首次收束前）")
        return 0

    all_errors: dict[str, list[str]] = {}
    for r in sorted(reports, key=lambda p: version_key(p.name)):
        errs = check_report(r)
        if errs:
            all_errors[r.name] = errs

    if all_errors:
        print("FAIL 收束报告结构/图表检查不通过：")
        for name, errs in all_errors.items():
            print(f"  {name}:")
            for e in errs:
                print(f"    - {e}")
        return 1

    print(f"OK 收束报告检查通过（{len(reports)} 份 v2.0+，含结构 + 图表）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
