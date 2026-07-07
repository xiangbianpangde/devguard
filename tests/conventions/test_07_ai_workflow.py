"""L4 规范测试 — 07-ai-workflow

对照 conventions/ai-workflow_AI协作开发流程/ 9 篇流程文档（v2.0 双轨制）+ README：
- 01-流程全景.md
- 02-模块分类.md
- 03-设计规范.md
- 04-长程开发.md
- 05-思考设计.md
- 06-端到端流程.md
- 07-验收交付.md
- 08-汇报收束.md
- 09-部署规范.md

检测 9 篇结构完整 + 关键内容存在 + README 5 条核心原则
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"

EXPECTED_DOCS = [
    "01-流程全景.md",
    "02-模块分类.md",
    "03-设计规范.md",
    "04-长程开发.md",
    "05-思考设计.md",
    "06-端到端流程.md",
    "07-验收交付.md",
    "08-汇报收束.md",
    "09-部署规范.md",
]


class TestAiWorkflowContracts:
    """07-ai-workflow 流程文档的 L4 检测（v2.0 双轨制）"""

    def test_all_nine_docs_exist(self):
        """9 篇流程文档 + README 必须全部存在"""
        missing = [d for d in EXPECTED_DOCS if not (WF_DIR / d).exists()]
        assert not missing, f"ai-workflow/ 缺流程文档：{missing}"
        assert (WF_DIR / "README.md").exists(), "ai-workflow/ 缺 README.md"

    def test_doc_01_defines_two_task_types(self):
        """01-流程全景：必须定义两类任务（长程 + 思考）"""
        content = (WF_DIR / "01-流程全景.md").read_text(encoding="utf-8")
        assert "长程" in content, "01 缺长程任务定义"
        assert "思考" in content, "01 缺思考任务定义"

    def test_doc_02_contains_module_classification(self):
        """02-模块分类：必须含工程模块 + 功能模块分类"""
        content = (WF_DIR / "02-模块分类.md").read_text(encoding="utf-8")
        assert "工程模块" in content, "02 缺工程模块"
        assert "功能模块" in content, "02 缺功能模块"

    def test_doc_03_contains_design_folder(self):
        """03-设计规范：必须含设计文件夹 7 件套结构"""
        content = (WF_DIR / "03-设计规范.md").read_text(encoding="utf-8")
        assert "设计文件夹" in content or "7 件套" in content, "03 缺设计文件夹结构"

    def test_doc_04_contains_long_running_flow(self):
        """04-长程开发：必须含 ADR + 预先计划"""
        content = (WF_DIR / "04-长程开发.md").read_text(encoding="utf-8")
        assert "ADR" in content, "04 缺 ADR"
        assert "预先计划" in content, "04 缺预先计划"

    def test_doc_05_contains_five_steps(self):
        """05-思考设计：必须含五步法"""
        content = (WF_DIR / "05-思考设计.md").read_text(encoding="utf-8")
        assert "五步" in content or "Step" in content, "05 缺五步法"

    def test_doc_06_contains_e2e_flow(self):
        """06-端到端流程：必须含 PRD + BDD + TDD"""
        content = (WF_DIR / "06-端到端流程.md").read_text(encoding="utf-8")
        assert "PRD" in content, "06 缺 PRD"
        assert "BDD" in content, "06 缺 BDD"
        assert "TDD" in content, "06 缺 TDD"

    def test_doc_07_contains_three_level_acceptance(self):
        """07-验收交付：必须含三级验收"""
        content = (WF_DIR / "07-验收交付.md").read_text(encoding="utf-8")
        assert "三级验收" in content or (
            "功能点级" in content and "收束节点级" in content
        ), "07 缺三级验收"

    def test_doc_08_contains_reporting_and_convergence(self):
        """08-汇报收束：必须含汇报 + 收束"""
        content = (WF_DIR / "08-汇报收束.md").read_text(encoding="utf-8")
        assert "汇报" in content, "08 缺汇报"
        assert "收束" in content, "08 缺收束"

    def test_doc_09_contains_deployment(self):
        """09-部署规范：必须含部署 + 服务器"""
        content = (WF_DIR / "09-部署规范.md").read_text(encoding="utf-8")
        assert "部署" in content, "09 缺部署"
        assert "服务器" in content, "09 缺服务器"

    def test_readme_contains_five_principles(self):
        """README：必须含 5 条核心原则"""
        content = (WF_DIR / "README.md").read_text(encoding="utf-8")
        for p in ["不越界", "不黑盒", "不断档", "不拖欠", "不积压"]:
            assert p in content, f"README 缺核心原则：{p}"
