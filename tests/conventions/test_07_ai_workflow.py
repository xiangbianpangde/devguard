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

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_DIR = REPO_ROOT / "conventions" / "ai-workflow_AI协作开发流程"
GATE_SCRIPT = REPO_ROOT / "scripts" / "check_convergence_gate.py"


def _load_gate():
    """加载 scripts/check_convergence_gate.py 作为模块（避免改 sys.path）"""
    spec = importlib.util.spec_from_file_location("check_convergence_gate", GATE_SCRIPT)
    assert spec and spec.loader, "无法加载 check_convergence_gate.py"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


class TestDocDefects:
    """更新后文档的回归检测（曾出现的缺陷不得复现）"""

    def test_doc_04_no_broken_user_file_safety_link(self):
        """04 §2.1 不得再链向不存在的 user-file-safety.md（死链）"""
        content = (WF_DIR / "04-第二步_迭代开发.md").read_text(encoding="utf-8")
        assert (
            "user-file-safety.md" not in content
        ), "04 仍引用不存在的 user-file-safety.md（应内联备份规则，不留死链）"
        assert "备份" in content, "04 §2.1 应保留'动本地文件前必备份'规则"

    def test_doc_05_balanced_code_fences(self):
        """05 的 markdown 代码围栏必须成对闭合"""
        content = (WF_DIR / "05-完整流程与核心原则.md").read_text(encoding="utf-8")
        assert content.count("```") % 2 == 0, "05 代码围栏不闭合（``` 数为奇数）"


class TestConvergenceGate:
    """收束闸门强制化（06 §2.1 硬闸门）的 L4 检测"""

    def test_gate_script_exists(self):
        """强制化脚本必须存在"""
        assert GATE_SCRIPT.exists(), "缺 scripts/check_convergence_gate.py"

    def test_devguard_plan_declares_tier_and_convergence(self):
        """dogfood：本仓库 docs/plan/开发清单.md 头部须声明 流程档位 + 收束间隔/节点"""
        gate = _load_gate()
        plan = REPO_ROOT / "docs" / "plan" / "开发清单.md"
        if not plan.exists():
            pytest.skip("本仓库无开发清单.md")
        text = plan.read_text(encoding="utf-8")
        assert gate.TIER_RE.search(text), "开发清单.md 头部缺 `> 流程档位:` 声明"
        assert gate.INTERVAL_RE.search(text) or gate.NODES_RE.search(
            text
        ), "开发清单.md 头部缺 `> 收束间隔:` 或 `> 收束节点:` 声明"

    def test_devguard_repo_passes_gate(self):
        """dogfood：本仓库当前状态应通过收束闸门"""
        gate = _load_gate()
        code, messages = gate.evaluate(
            REPO_ROOT / "docs" / "plan" / "开发清单.md",
            REPO_ROOT / "docs" / "reports",
        )
        assert code == 0, f"本仓库未通过收束闸门：{messages}"

    def test_gate_fails_on_missing_header(self, tmp_path):
        """缺头部声明 → 闸门拦截（退出码 1）"""
        gate = _load_gate()
        plan = tmp_path / "开发清单.md"
        plan.write_text(
            "# 开发清单\n\n| # | 功能点 | 状态 |\n|---|---|---|\n" "| 1 | A | ✅ |\n",
            encoding="utf-8",
        )
        code, _ = gate.evaluate(plan, tmp_path / "reports")
        assert code == 1, "缺 流程档位/收束声明 应拦截"

    def test_gate_fails_when_node_crossed_without_report(self, tmp_path):
        """完成数跨过收束节点但无收束报告 → 闸门拦截"""
        gate = _load_gate()
        plan = tmp_path / "开发清单.md"
        rows = "".join(f"| {i} | F{i} | ✅ |\n" for i in range(1, 7))  # 6 完成
        plan.write_text(
            "# 开发清单\n> 流程档位: 标准\n> 收束间隔: 3\n\n"
            "| # | 功能点 | 状态 |\n|---|---|---|\n" + rows,
            encoding="utf-8",
        )
        reports = tmp_path / "reports"
        reports.mkdir()
        code, msgs = gate.evaluate(plan, reports)
        assert code == 1, f"6 完成 / 间隔 3 / 0 报告 应拦截，得到 {msgs}"

    def test_gate_passes_when_reports_sufficient(self, tmp_path):
        """收束报告数足够覆盖跨过的节点 → 通过"""
        gate = _load_gate()
        plan = tmp_path / "开发清单.md"
        rows = "".join(f"| {i} | F{i} | ✅ |\n" for i in range(1, 7))  # 6 完成
        plan.write_text(
            "# 开发清单\n> 流程档位: 标准\n> 收束间隔: 3\n\n"
            "| # | 功能点 | 状态 |\n|---|---|---|\n" + rows,
            encoding="utf-8",
        )
        reports = tmp_path / "reports"
        reports.mkdir()
        (reports / "收束报告-v0.1.md").write_text("x", encoding="utf-8")
        (reports / "收束报告-v0.2.md").write_text("x", encoding="utf-8")
        code, msgs = gate.evaluate(plan, reports)
        assert code == 0, f"6 完成 / 间隔 3 / 2 报告 应通过，得到 {msgs}"

    def test_gate_na_when_no_plan(self, tmp_path):
        """无开发清单.md 的仓库视为 N/A，通过"""
        gate = _load_gate()
        code, _ = gate.evaluate(tmp_path / "缺.md", tmp_path / "reports")
        assert code == 0, "无 plan 应判 N/A 通过"
