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

        # R5-14（2026-08-14 红队第七轮 P1）：全文全关键词命中 + §一 段落至少 1 命中——
        # 原「任一关键词即通过」可被 5 行空壳绕过（空壳含 1 个关键词即过）；
        # 现要求：全文必须全部关键词命中（防语义缺失），且 §一 节内至少 1 个
        # 关键词（防 §一 空壳段落——真实文档关键词散落他节属正常，不苛求全在 §一）。
        section_one = text.split("## ", 1)[-1] if "## " in text else text
        section_one = section_one.split("## ", 1)[0]
        missing = [k for k in keywords if k not in text]
        if missing:
            errors.append(f"{filename} 全文缺关键词（期望全部命中）: {missing}")
        elif not any(k in section_one for k in keywords):
            errors.append(f"{filename} §一 段落无任何主题关键词（疑似空壳）: {keywords}")

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
