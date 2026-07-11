"""check_doc_quality.py — 文档质量 L1 检测（图表 + 段落精简）

检查 docs/reports/ 下 v2.0+ .md 报告：
- 含图表: ≥1 mermaid 代码块 或 ≥2 表格（|---|）
- 段落精简: 无 >15 行连续非空行（避免文字堆砌）

对应规范：06-documentation §三配图规约（扩展为汇报/报告必备图表）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / "docs" / "reports"
REPORT_NAME = re.compile(r"^收束报告-v(?P<major>\d+)\.(?P<minor>\d+)\.md$")


def version_key(name: str) -> tuple[int, ...]:
    match = REPORT_NAME.fullmatch(name)
    return (int(match.group("major")), int(match.group("minor"))) if match else (0, 0)


def check_doc(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    mermaid = text.count("```mermaid")
    tables = text.count("|---|")
    if mermaid < 1 and tables < 2:
        errors.append(
            f"图表不足: mermaid {mermaid}, 表格 {tables}（需 ≥1 mermaid 或 ≥2 表格）"
        )

    para_len = 0
    for line in text.split("\n"):
        if line.strip():
            para_len += 1
            if para_len > 15:
                errors.append("段落过长（>15 行连续非空行，文字堆砌）")
                break
        else:
            para_len = 0

    return errors


def main() -> int:
    candidates = list(REPORTS_DIR.glob("收束报告-*.md"))
    invalid_names = sorted(
        path.name for path in candidates if not REPORT_NAME.fullmatch(path.name)
    )
    if invalid_names:
        print(f"FAIL 收束报告文件名不符合 收束报告-vN.N.md: {invalid_names}")
        return 1
    docs = [p for p in candidates if version_key(p.name) >= (2, 0)]
    if not docs:
        print("OK 无 v2.0+ 报告（首次收束前）")
        return 0

    all_errors: dict[str, list[str]] = {}
    for d in sorted(docs, key=lambda p: version_key(p.name)):
        errs = check_doc(d)
        if errs:
            all_errors[d.name] = errs

    if all_errors:
        print("FAIL 文档质量检查不通过：")
        for name, errs in all_errors.items():
            print(f"  {name}:")
            for e in errs:
                print(f"    - {e}")
        return 1

    print(f"OK 文档质量检查通过（{len(docs)} 份 v2.0+，含图表 + 段落精简）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
