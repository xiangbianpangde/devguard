"""L4 规范测试 — 07-ai-workflow

对照 conventions/ai-workflow_AI协作开发流程/ 7 篇流程文档：
- 01-角色分工与文件体系.md
- 02-第零步_调研.md
- 03-第一步_编写计划.md
- 04-第二步_迭代开发.md
- 05-完整流程与核心原则.md
- 06-第三步_收束节点.md
- 07-汇报.md

检测 7 篇结构完整 + 关键内容存在
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

EXPECTED_DOCS = [
    "01-角色分工与文件体系.md",
    "02-第零步_调研.md",
    "03-第一步_编写计划.md",
    "04-第二步_迭代开发.md",
    "05-完整流程与核心原则.md",
    "06-第三步_收束节点.md",
    "07-汇报.md",
]


class TestAiWorkflowContracts:
    """07-ai-workflow 流程文档的 L4 检测"""

    def test_all_seven_docs_exist(self):
        """7 篇流程文档必须全部存在"""
        missing = [d for d in EXPECTED_DOCS if not (WF_DIR / d).exists()]
        assert not missing, f"ai-workflow/ 缺流程文档：{missing}"

    def test_doc_01_defines_three_roles(self):
        """01-角色分工：必须定义 3 个角色（审查者/架构师+开发/决策者）"""
        path = WF_DIR / "01-角色分工与文件体系.md"
        content = path.read_text(encoding="utf-8")
        for role in ["审查者", "架构师", "决策者"]:
            assert role in content, f"01 缺角色：{role}"

    def test_doc_02_contains_research(self):
        """02-第零步：必须提到调研（research）"""
        path = WF_DIR / "02-第零步_调研.md"
        content = path.read_text(encoding="utf-8")
        assert "调研" in content or "research" in content.lower(), "02 缺调研定义"

    def test_doc_04_contains_dev_loop(self):
        """04-第二步：必须提到迭代开发循环（开发循环 / 8 步）"""
        path = WF_DIR / "04-第二步_迭代开发.md"
        content = path.read_text(encoding="utf-8")
        # 检查开发循环或 8 步（扫描/实现/验证/审查/人/更新/commit/回顾）
        for step in ["扫描", "实现", "验证", "审查", "commit", "回顾"]:
            assert step in content, f"04 缺开发循环步骤：{step}"

    def test_doc_05_contains_five_principles(self):
        """05-完整流程：必须包含 5 条核心原则（不越界/不黑盒/不断档/不拖欠/不积压）"""
        path = WF_DIR / "05-完整流程与核心原则.md"
        content = path.read_text(encoding="utf-8")
        for p in ["不越界", "不黑盒", "不断档", "不拖欠", "不积压"]:
            assert p in content, f"05 缺核心原则：{p}"

    def test_doc_06_contains_convergence(self):
        """06-第三步：必须提到收束节点（convergence gate）"""
        path = WF_DIR / "06-第三步_收束节点.md"
        content = path.read_text(encoding="utf-8")
        assert "收束" in content, "06 缺收束节点定义"

    def test_doc_07_contains_two_tier_reporting(self):
        """07-汇报：必须提到两档汇报（功能点级 + 收束报告）"""
        path = WF_DIR / "07-汇报.md"
        content = path.read_text(encoding="utf-8")
        assert (
            "功能点" in content and "收束" in content
        ), "07 缺两档汇报（功能点 + 收束）"
