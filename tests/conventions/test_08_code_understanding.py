"""L4 规范测试 — 08-code-understanding

对照 conventions/08-code-understanding_代码理解与图谱规范.md：
- 核心洞察：双图谱（CodeGraph 给 AI + Understand-Anything 给人）
- 启用门槛：分线（CodeGraph 需 > 10 模块或 > 5 万行；Understand-Anything 任何代码）
- 单一权威：本规范管 2 套独立图谱，调用图相关去重映射见此
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONV_08 = REPO_ROOT / "conventions" / "08-code-understanding_代码理解与图谱规范.md"
CALL_GRAPH_EXAMPLE = REPO_ROOT / "src" / "code-understanding" / "call_graph_example.py"


class TestCodeUnderstandingContracts:
    """08-code-understanding 的 L4 检测"""

    def test_spec_mentions_dual_graphs(self):
        """核心洞察：08 规范必须明确提到双图谱（CodeGraph + Understand-Anything）"""
        content = CONV_08.read_text(encoding="utf-8")
        assert "CodeGraph" in content, "08 规范缺 CodeGraph（AI 图谱）"
        assert (
            "Understand-Anything" in content
        ), "08 规范缺 Understand-Anything（人图谱）"

    def test_spec_distinguishes_ai_vs_human(self):
        """核心洞察：08 规范必须明确区分 AI 消费者 vs 人消费者"""
        content = CONV_08.read_text(encoding="utf-8")
        # 检查有"AI" 和 "人" 对比
        assert (
            "AI" in content and "人" in content
        ), "08 规范缺 AI vs 人 消费者区分（核心洞察：两套图谱）"

    def test_spec_has_threshold_for_codegraph(self):
        """启用门槛：CodeGraph 引入门槛必须具体（> 10 模块 或 > 5 万行）"""
        content = CONV_08.read_text(encoding="utf-8")
        assert (
            "10" in content and "5" in content
        ), "08 规范缺 CodeGraph 引入门槛（> 10 模块 或 > 5 万行）"

    @pytest.mark.skipif(
        not CALL_GRAPH_EXAMPLE.exists(),
        reason="src/code-understanding/call_graph_example.py 不存在",
    )
    def test_call_graph_example_exists(self):
        """教学示例：call_graph_example.py 必须存在（演示 AST 调用图）"""
        content = CALL_GRAPH_EXAMPLE.read_text(encoding="utf-8")
        # 应该演示 AST 遍历
        assert "ast" in content, "call_graph_example.py 缺 ast 导入（应演示 AST 遍历）"

    def test_spec_mentions_mcp_or_api(self):
        """08 规范应提到 MCP / API（CodeGraph 给 AI 的访问方式）"""
        content = CONV_08.read_text(encoding="utf-8")
        assert (
            "MCP" in content or "API" in content or "tool" in content.lower()
        ), "08 规范缺 MCP/API 描述（CodeGraph 给 AI 用的接口）"
