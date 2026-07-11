"""L4 规范测试 — 05-testing

对照 conventions/05-testing_测试规范.md §一 红线 1-5：
1. 测试独立，不依赖执行顺序 → pytest -p no:randomly 乱序跑全绿
2. 只 Mock 外部边界（DB/HTTP/文件/时间）→ 审查
3. 覆盖正常 + 边界 + 异常路径 → 审查 + 分支覆盖率
4. 无 flaky test → CI 重试检测
5. 开发按 BDD+TDD 流程 → 审查 + 测试用例 ↔ BDD 一一对应
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
CONV_05 = REPO_ROOT / "conventions" / "05-testing_测试规范.md"
SPECS_DIR = REPO_ROOT / "docs" / "specs"
L4_TESTS_DIR = REPO_ROOT / "tests" / "conventions"


class TestTestingContracts:
    """05-testing §一 红线 1-5 的 L4 检测"""

    def test_pytest_config_exists(self):
        """L1 检测：pyproject.toml（pytest 配置）必须存在"""
        assert PYPROJECT.exists(), "pyproject.toml 缺失——pytest 无配置"

    def test_pytest_testpaths_defined(self):
        """pytest 必须配置 testpaths 指向 tests 目录"""
        content = PYPROJECT.read_text(encoding="utf-8")
        assert (
            "testpaths" in content
        ), "pyproject.toml 缺 [tool.pytest.ini_options] testpaths 配置"

    def test_pytest_collection_runs_clean(self):
        """红线 1：pytest 收集能跑通（不依赖执行顺序：每次 collect 顺序可能不同）"""
        # 跑两次 collect，验证每次都能收集所有测试
        result1 = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        result2 = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert (
            result1.returncode == 0 and result2.returncode == 0
        ), f"pytest --collect-only 失败：\n{result1.stderr}\n{result2.stderr}"
        # 两次收集到的测试数应该相同
        n1 = result1.stdout.count("::")
        n2 = result2.stdout.count("::")
        assert (
            n1 == n2 and n1 > 0
        ), f"pytest 收集不稳定（第一次 {n1}，第二次 {n2}）—— 红线 1：测试可能依赖执行顺序"

    def test_l4_tests_for_every_convention(self):
        """红线 5（BDD+TDD）：每篇规范必须至少有 1 个 L4 test。

        治理能力可以继续增加独立契约测试，不能把新增测试误判为漂移。
        """
        if not L4_TESTS_DIR.exists():
            pytest.fail("tests/conventions/ 缺失——L4 规范测试不存在")
        existing = sorted(p.stem for p in L4_TESTS_DIR.glob("test_*.py"))
        expected = sorted(
            [
                "test_01_architecture",
                "test_02_coding",
                "test_03_git",
                "test_04_api",
                "test_05_testing",
                "test_06_documentation",
                "test_07_ai_workflow",
                "test_08_code_understanding",
                "test_perf_baseline",  # V2.5: 性能基线
                "test_meta_l1_check",  # V4.4: _meta.yaml l1_check 字段一致性
                "test_status",  # V2.1 #40: STATUS.md 章节级 L1
                "test_claude",  # V2.1 #41: CLAUDE.md 结构 L1
                "test_plan",  # V2.1 #42: 开发清单格式 L1
                "test_file_placement",  # V2.1 #45 强化: 文件放置规则 L1
                "test_exemption_log",  # V2.3 #51: 豁免登记强制化
                "test_updated_tag",  # V2.3 #53: 更新时间标签强制化
                "test_convergence_gate",  # V2.3 #52: 收束硬闸门
                "test_html_artifact",  # V2.3 #48: HTML 产出物结构校验
                "test_decision_alignment",  # V2.3 #50: 决策对齐拦开工
                "test_doc_sync",  # V2.3 阶段C 补遗: 四件套硬同步
                "test_scaffold",  # V2.3 #49: 基准约束脚手架
            ]
        )
        missing = set(expected) - set(existing)
        assert not missing, (
            f"L4 核心测试缺失（实际 {len(existing)}，"
            f"核心期望 {len(expected)}）：{missing}"
        )

    def test_redline_2_mock_boundary_documented(self):
        """红线 2（只 Mock 外部边界）必须在 05 §三 决策表有文档化"""
        content = CONV_05.read_text(encoding="utf-8")
        assert (
            "外部" in content and "Mock" in content
        ), "05 §三 决策表缺 Mock 边界指引（红线 2：只 Mock 外部边界）"

    def test_redline_3_coverage_paths_documented(self):
        """红线 3（正常 + 边界 + 异常路径）必须在 05 §三 决策表有文档化"""
        content = CONV_05.read_text(encoding="utf-8")
        assert (
            "边界" in content and "异常" in content
        ), "05 §三 决策表缺三路径覆盖指引（红线 3：正常+边界+异常）"

    def test_redline_5_bdd_specs_exist(self):
        """红线 5（BDD+TDD）：docs/specs/ 至少有 BDD 规格"""
        if not SPECS_DIR.exists():
            pytest.skip("docs/specs/ 不存在（v0.1 项目可能未建 BDD）")
        bdd_files = list(SPECS_DIR.glob("**/*.md")) + list(
            SPECS_DIR.glob("**/*.feature")
        )
        assert (
            bdd_files
        ), "docs/specs/ 没有 BDD 规格文件（红线 5：开发按 BDD+TDD 流程，缺 BDD 源）"
