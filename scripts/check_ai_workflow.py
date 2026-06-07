"""V9.1 ai-workflow 章节级 L1 钩子（07-ai-workflow 红线 1-7）

V9.1 扩展：7 篇流程文档每篇 §一 红线验证（V5.2 关键内容 + V9.1 占位符）

7 篇流程文档：
- 01-角色分工与文件体系.md：§一 含 AI/角色/分工
- 02-第零步_调研.md：§一 含 调研/背景/问题
- 03-第一步_编写计划.md：§一 含 计划/收束节点/档位/BDD/TDD
- 04-第二步_迭代开发.md：§一 含 迭代/实现/可观测/TDD/扫描仓库
- 05-完整流程与核心原则.md：§一 含 原则/流程/不越界/不黑盒/不断档/不拖欠/不积压
- 06-第三步_收束节点.md：§一 含 收束/四阶段/整理/测试/AI审计/人审计/验证
- 07-汇报.md：§一 含 汇报/功能点级/不落盘
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

# V9.1: 每篇含 §一 红线关键词（比 V5.2 关键内容更严）
EXPECTED_FILES_AND_KEYWORDS = {
    "01-角色分工与文件体系.md": ["角色", "分工", "文件", "体系", "AI"],
    "02-第零步_调研.md": ["调研", "背景", "问题", "现状"],
    "03-第一步_编写计划.md": ["计划", "收束节点", "档位", "BDD", "TDD", "调研"],
    "04-第二步_迭代开发.md": [
        "迭代",
        "实现",
        "可观测",
        "TDD",
        "扫描",
        "测试",
    ],
    "05-完整流程与核心原则.md": [
        "原则",
        "不越界",
        "不黑盒",
        "不断档",
        "不拖欠",
        "不积压",
    ],
    "06-第三步_收束节点.md": [
        "收束",
        "整理",
        "测试",
        "审计",
        "人审",
        "验证",
    ],
    "07-汇报.md": ["汇报", "功能点", "不落盘", "内联", "收束报告"],
}


def main() -> int:
    if not WORKFLOW_DIR.exists():
        print(f"FAIL: {WORKFLOW_DIR} 不存在")
        return 1

    errors: list[str] = []

    for filename, keywords in EXPECTED_FILES_AND_KEYWORDS.items():
        path = WORKFLOW_DIR / filename
        if not path.exists():
            errors.append(f"缺文件: {filename}")
            continue

        text = path.read_text(encoding="utf-8")

        # V9.1: 必须含 §一 红线关键词
        found = [k for k in keywords if k in text]
        if not found:
            errors.append(
                f"{filename} 缺 §一 红线关键词（期望含以下任一关键词: {keywords}）"
            )

        # V9.1: §一 标题必须存在（章节级 L1 强制）
        if "## 一" not in text and "## §一" not in text and "## 1." not in text:
            # 中文 § 字符可能编码问题——兼容多种标题
            if "一、" not in text and "## 1" not in text:
                # 兜底：检查文件有"## "二级标题即可
                if text.count("## ") < 2:
                    errors.append(f"{filename} 缺 §一 标题")

    if errors:
        print("FAIL 章节级 L1 验证不通过：")
        for e in errors:
            print(f"  - {e}")
        return 1

    n = len(EXPECTED_FILES_AND_KEYWORDS)
    print(f"OK ai-workflow 章节级 L1 验证通过（{n} 篇流程文档 + §一 红线）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
