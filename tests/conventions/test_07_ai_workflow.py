"""L4 规范测试 — 07-ai-workflow（v2.0 9 篇对齐）

对照 conventions/ai-workflow_AI协作开发流程/ 新 9 篇流程文档：
- 01-流程全景.md
- 02-模块分类.md
- 03-设计规范.md
- 04-长程开发.md
- 05-思考设计.md
- 06-端到端流程.md
- 07-验收交付.md
- 08-汇报收束.md
- 09-部署规范.md

检测 9 篇结构完整 + 关键内容存在 + 五核心原则归口 README。
"""

from __future__ import annotations

from pathlib import Path

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


def _read(name: str) -> str:
    return (WF_DIR / name).read_text(encoding="utf-8")


class TestAiWorkflowContracts:
    """07-ai-workflow v2.0 流程文档的 L4 检测"""

    def test_all_nine_docs_exist(self):
        """9 篇流程文档必须全部存在"""
        missing = [d for d in EXPECTED_DOCS if not (WF_DIR / d).exists()]
        assert not missing, f"ai-workflow/ 缺流程文档：{missing}"

    def test_doc_01_two_task_types(self):
        """01-流程全景：必须定义两类任务（长程 / 思考）"""
        content = _read("01-流程全景.md")
        for kw in ["两类任务", "长程", "思考"]:
            assert kw in content, f"01 缺关键词：{kw}"

    def test_doc_02_module_classification(self):
        """02-模块分类：必须区分工程模块 / 基础模块 / 功能模块"""
        content = _read("02-模块分类.md")
        for kw in ["工程模块", "基础模块", "功能模块"]:
            assert kw in content, f"02 缺模块类型：{kw}"

    def test_doc_03_design_folder(self):
        """03-设计规范：必须定义设计文件夹（简报/实现计划/阅读笔记）"""
        content = _read("03-设计规范.md")
        for kw in ["简报", "实现计划", "阅读笔记"]:
            assert kw in content, f"03 缺设计件套：{kw}"

    def test_doc_04_long_running(self):
        """04-长程开发：必须含 AI决策 / 验收 / TDD"""
        content = _read("04-长程开发.md")
        for kw in ["决策", "验收", "TDD"]:
            assert kw in content, f"04 缺长程要素：{kw}"

    def test_doc_05_thinking(self):
        """05-思考设计：必须含讨论 Agent 五步法（笔记/引导）"""
        content = _read("05-思考设计.md")
        for kw in ["思考", "笔记", "引导"]:
            assert kw in content, f"05 缺思考要素：{kw}"

    def test_doc_06_end_to_end(self):
        """06-端到端流程：必须含 PRD / BDD / 部署 / 交付"""
        content = _read("06-端到端流程.md")
        for kw in ["PRD", "BDD", "部署", "交付"]:
            assert kw in content, f"06 缺端到端环节：{kw}"

    def test_doc_07_acceptance(self):
        """07-验收交付：必须含三级验收（功能点 / 收束 / 交付物）"""
        content = _read("07-验收交付.md")
        for kw in ["验收", "功能点", "收束", "交付物"]:
            assert kw in content, f"07 缺验收要素：{kw}"

    def test_doc_08_reporting_convergence(self):
        """08-汇报收束：必须含汇报 + 收束 + ADR"""
        content = _read("08-汇报收束.md")
        for kw in ["汇报", "功能点", "收束", "ADR"]:
            assert kw in content, f"08 缺汇报收束要素：{kw}"

    def test_doc_09_deployment(self):
        """09-部署规范：必须含统一服务器部署 + 监控"""
        content = _read("09-部署规范.md")
        for kw in ["部署", "统一服务器", "监控"]:
            assert kw in content, f"09 缺部署要素：{kw}"

    def test_five_principles_in_readme(self):
        """五核心原则（不越界/不黑盒/不断档/不拖欠/不积压）归口 README"""
        content = _read("README.md")
        for p in ["不越界", "不黑盒", "不断档", "不拖欠", "不积压"]:
            assert p in content, f"README 缺核心原则：{p}"
