"""V5.2 ai-workflow 章节级 L1 钩子（07-ai-workflow 红线 1-7）

验证 ai-workflow 流程文档的 7 篇都存在 + 每篇关键内容覆盖。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

# 7 篇流程文档 + 关键内容关键词（每篇至少含 1 个关键词）
EXPECTED_FILES_AND_KEYWORDS = {
    "01-角色分工与文件体系.md": ["角色", "文件体系", "AI"],
    "02-第零步_调研.md": ["调研", "背景", "问题"],
    "03-第一步_编写计划.md": ["计划", "收束节点", "档位", "BDD"],
    "04-第二步_迭代开发.md": ["迭代", "实现", "可观测", "TDD"],
    "05-完整流程与核心原则.md": ["原则", "流程", "不越界", "不黑盒"],
    "06-第三步_收束节点.md": ["收束", "四阶段", "整理", "测试", "审计", "验证"],
    "07-汇报.md": ["汇报", "功能点", "不落盘", "收束报告"],
}


def main() -> int:
    if not WORKFLOW_DIR.exists():
        print(f"FAIL: {WORKFLOW_DIR} 不存在")
        return 1

    errors: list[str] = []

    # 1) 文件存在
    for filename in EXPECTED_FILES_AND_KEYWORDS:
        path = WORKFLOW_DIR / filename
        if not path.exists():
            errors.append(f"缺文件: {filename}")

    # 2) 关键内容存在
    for filename, keywords in EXPECTED_FILES_AND_KEYWORDS.items():
        path = WORKFLOW_DIR / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found = any(kw in text for kw in keywords)
        if not found:
            errors.append(f"{filename} 缺关键内容（期望含以下任一关键词: {keywords}）")

    if errors:
        print("FAIL 章节级 L1 验证不通过：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"OK ai-workflow 章节级 L1 验证通过（{len(EXPECTED_FILES_AND_KEYWORDS)} 篇流程文档）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
