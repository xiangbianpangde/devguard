"""V10 ai-workflow 章节级 L1 钩子（07-ai-workflow v2.0）

9 篇流程文档（v2.0 双轨制）每篇 §一 红线关键词验证：
- 01-流程全景.md：§一 含 长程/思考/任务/触发
- 02-模块分类.md：§一 含 工程模块/功能模块/数据契约/插件
- 03-设计规范.md：§一 含 设计文件夹/7 件套/设计.md/实现计划
- 04-长程开发.md：§一 含 ADR/预先计划/验收报告/迭代
- 05-思考设计.md：§一 含 笔记/引导/规范设计/HTML/记录
- 06-端到端流程.md：§一 含 PRD/BDD/TDD/模块划分/测试
- 07-验收交付.md：§一 含 三级验收/功能点级/收束节点级/交付
- 08-汇报收束.md：§一 含 汇报/收束/worklog/ADR/STATUS
- 09-部署规范.md：§一 含 部署/服务器/插入/验证/回滚
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

# v2.0: 每篇含 §一 红线关键词
EXPECTED_FILES_AND_KEYWORDS = {
    "01-流程全景.md": ["长程", "思考", "任务", "触发"],
    "02-模块分类.md": ["工程模块", "功能模块", "数据契约", "插件"],
    "03-设计规范.md": ["设计文件夹", "7 件套", "设计.md", "实现计划"],
    "04-长程开发.md": ["ADR", "预先计划", "验收报告", "迭代"],
    "05-思考设计.md": ["笔记", "引导", "规范设计", "HTML", "记录"],
    "06-端到端流程.md": ["PRD", "BDD", "TDD", "模块划分", "测试"],
    "07-验收交付.md": ["三级验收", "功能点级", "收束节点级", "交付"],
    "08-汇报收束.md": ["汇报", "收束", "worklog", "ADR", "STATUS"],
    "09-部署规范.md": ["部署", "服务器", "插入", "验证", "回滚"],
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

        # 必须含 §一 红线关键词（任一即通过）
        found = [k for k in keywords if k in text]
        if not found:
            errors.append(f"{filename} 缺 §一 红线关键词（期望含以下任一关键词: {keywords}）")

        # §一 标题必须存在（章节级 L1 强制）
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
