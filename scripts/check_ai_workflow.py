"""ai-workflow 章节级 L1 钩子（07-ai-workflow §一 红线，v2.0 9 篇对齐）

v2.0 流程重构后，ai-workflow_AI协作开发流程/ 由旧 7 篇改为新 9 篇：
- 01-流程全景.md      ：§一 两类任务（长程 / 思考）
- 02-模块分类.md      ：§一 工程模块 vs 基础+功能模块
- 03-设计规范.md      ：§一 设计文件夹 7 件套（简报/设计/实现计划/阅读笔记）
- 04-长程开发.md      ：§一 AI决策→预先计划→验收报告 + TDD
- 05-思考设计.md      ：§一 讨论 Agent 五步法（笔记/引导）
- 06-端到端流程.md    ：§一 PRD→BDD→…→部署→交付
- 07-验收交付.md      ：§一 三级验收（功能点级/收束节点级/项目级）+ 交付物
- 08-汇报收束.md      ：§一 汇报类型 + 收束节点 + ADR
- 09-部署规范.md      ：§一 统一服务器（max）部署 + 监控

五核心原则（不越界/不黑盒/不断档/不拖欠/不积压）现归口 README.md，单独校验。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

# 每篇必须命中的 §一 红线关键词（全部命中才算通过）
EXPECTED_FILES_AND_KEYWORDS = {
    "01-流程全景.md": ["两类任务", "长程", "思考"],
    "02-模块分类.md": ["工程模块", "基础模块", "功能模块"],
    "03-设计规范.md": ["简报", "设计", "实现计划", "阅读笔记"],
    "04-长程开发.md": ["长程", "决策", "验收", "TDD"],
    "05-思考设计.md": ["思考", "笔记", "引导"],
    "06-端到端流程.md": ["PRD", "BDD", "部署", "交付"],
    "07-验收交付.md": ["验收", "功能点", "收束", "交付物"],
    "08-汇报收束.md": ["汇报", "功能点", "收束", "ADR"],
    "09-部署规范.md": ["部署", "统一服务器", "监控"],
}

# 五核心原则归口 README.md（v2.0 从编号文档移出）
FIVE_PRINCIPLES = ["不越界", "不黑盒", "不断档", "不拖欠", "不积压"]


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

        # 每篇必须命中全部 §一 红线关键词
        missing = [k for k in keywords if k not in text]
        if missing:
            errors.append(f"{filename} 缺 §一 红线关键词: {missing}")

        # §一 标题必须存在（章节级 L1 强制；兼容多种写法）
        if (
            "## 一" not in text
            and "## §一" not in text
            and "## 1." not in text
            and "一、" not in text
        ):
            if text.count("## ") < 2:
                errors.append(f"{filename} 缺 §一 标题")

    # 五核心原则：归口 README.md
    readme = WORKFLOW_DIR / "README.md"
    if not readme.exists():
        errors.append("缺文件: README.md")
    else:
        rtext = readme.read_text(encoding="utf-8")
        miss_p = [p for p in FIVE_PRINCIPLES if p not in rtext]
        if miss_p:
            errors.append(f"README.md 缺五核心原则: {miss_p}")

    if errors:
        print("FAIL 章节级 L1 验证不通过：")
        for e in errors:
            print(f"  - {e}")
        return 1

    n = len(EXPECTED_FILES_AND_KEYWORDS)
    print(f"OK ai-workflow 章节级 L1 验证通过（{n} 篇流程文档 + §一 红线 + 五原则）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
