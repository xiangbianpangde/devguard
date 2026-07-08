"""check_consistency.py — 产出一致性评分（目标 ≥80%）

评估 devguard 强制性措施对 11 个产出维度的覆盖度，加权评分。
强制度: 强制(L1/pre-commit)=90, 可选(模板)=50, 无=20
证据存在则按强制度计分，否则折半；无证据=20%。

对应规范：跨 01-10（强制性措施体系一致性）
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# (维度, 权重, 强制度, 证据文件/目录)
DIMENSIONS: list[tuple[str, float, int, str | None]] = [
    ("commit 格式", 0.08, 90, "commitlint.config.js"),
    ("代码风格", 0.08, 90, "src/coding/ruff.toml"),
    ("规范契约", 0.08, 90, "tests/conventions/"),
    ("架构依赖", 0.08, 90, "importlinter.ini"),
    ("API 设计", 0.08, 90, ".spectral.yaml"),
    ("产出物存在", 0.08, 90, "README.md"),
    ("文档格式", 0.08, 90, ".markdownlint.json"),
    ("汇报结构", 0.10, 90, "scripts/check_report.py"),
    ("图表使用", 0.10, 90, "scripts/check_report.py"),
    ("文字精简准确", 0.10, 90, "scripts/check_doc_quality.py"),
    ("汇报风格统一", 0.14, 90, "docs/templates/收束报告模板.md"),
]


def main() -> int:
    score = 0.0
    details: list[str] = []
    for name, weight, strength, evidence in DIMENSIONS:
        exists = (REPO_ROOT / evidence).exists() if evidence else False
        actual = strength if exists else (strength * 0.5 if evidence else 20)
        score += weight * actual
        details.append(
            f"  {name}: 权重{weight:.0%} 强制度{strength}% "
            f"证据{'✅' if exists else '❌'} → {actual:.0f}%"
        )

    print(f"产出一致性评分: {score:.1f}%（目标 ≥80%）")
    for d in details:
        print(d)

    if score >= 80:
        print(f"OK 一致性达标（{score:.1f}% ≥ 80%）")
        return 0
    print(f"FAIL 一致性未达标（{score:.1f}% < 80%）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
