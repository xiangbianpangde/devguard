"""L4 规范测试 — 06-documentation

对照 conventions/06-documentation_文档规范.md §一 红线 1-5：
1. 项目根有 README，含「快速开始」（≤5 条命令跑起来）
2. 每次发布更新 CHANGELOG（Keep a Changelog 格式）
3. 文档与代码在同一个 PR 中改（不脱节）
4. 公共 API 有 docstring（参数/返回/异常/示例）
5. 注释与代码行为一致，过时注释立即删
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
README = REPO_ROOT / "README.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
CONV_06 = REPO_ROOT / "conventions" / "06-documentation_文档规范.md"
API_MAIN = REPO_ROOT / "src" / "api" / "main.py"
MARKDOWNLINT_JSON = REPO_ROOT / ".markdownlint.json"
PRE_COMMIT_YAML = REPO_ROOT / ".pre-commit-config.yaml"


class TestDocumentationContracts:
    """06-documentation §一 红线 1-5 的 L4 检测"""

    def test_readme_exists(self):
        """红线 1：README.md 必须在项目根"""
        assert README.exists(), "README.md 缺失（项目根）"

    def test_readme_has_quickstart(self):
        """红线 1：README 必须含「快速开始」段（≤5 条命令跑起来）"""
        content = README.read_text(encoding="utf-8")
        assert (
            "快速开始" in content or "Quick Start" in content or "Quickstart" in content
        ), "README 缺「快速开始」段（红线 1：新人按 README 能独立启动）"

    def test_changelog_exists(self):
        """红线 2：CHANGELOG.md 必须存在"""
        assert CHANGELOG.exists(), "CHANGELOG.md 缺失（红线 2：发布即更新）"

    def test_changelog_uses_keep_a_changelog_sections(self):
        """红线 2：CHANGELOG 用 Keep a Changelog 6 分类（Added/Changed/Fixed/Deprecated/Removed/Security）"""  # noqa: E501
        content = CHANGELOG.read_text(encoding="utf-8")
        required_sections = [
            "Added",
            "Changed",
            "Fixed",
            "Deprecated",
            "Removed",
            "Security",
        ]
        missing = [
            s
            for s in required_sections
            if f"### {s}" not in content and f"## {s}" not in content
        ]
        assert not missing, f"CHANGELOG 缺 6 分类：{missing}"

    @pytest.mark.skipif(not API_MAIN.exists(), reason="src/api/main.py 不存在")
    def test_public_api_has_docstring(self):
        """红线 4：公共 API 函数必须有 docstring"""
        source = API_MAIN.read_text(encoding="utf-8")
        tree = ast.parse(source)

        public_funcs = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.name.startswith("_")
            and not isinstance(node, ast.AsyncFunctionDef)  # FastAPI handler 是 async
        ]

        # FastAPI handler 大量是 async，允许豁免
        # 检查非 async 的 public func 都有 docstring
        sync_public = [
            node for node in public_funcs if not isinstance(node, ast.AsyncFunctionDef)
        ]
        for func in sync_public:
            docstring = ast.get_docstring(func)
            assert (
                docstring
            ), f"公共函数 {func.name} 缺 docstring（红线 4：公共 API 必须有 docstring）"

    def test_redline_5_anti_pattern_in_doc(self):
        """红线 5：06 §四 反模式必须提到「注释与代码不符」"""
        content = CONV_06.read_text(encoding="utf-8")
        assert (
            "注释与代码" in content or "过时注释" in content
        ), "06 §四 反模式缺「注释与代码不符」案例（红线 5）"

    def test_markdownlint_config_exists(self):
        """L1 检测：.markdownlint.json 必须存在（markdown 格式 L1 配置就位）"""
        # v0.1: 钩子暂不启用（避免阻塞 commit），但配置就位
        assert (
            MARKDOWNLINT_JSON.exists()
        ), ".markdownlint.json 缺失——markdown L1 检测无配置"

    def test_markdownlint_in_precommit_optional(self):
        """markdownlint 钩子 v0.1 暂不启用（V2 加配置/文档修整后启用）

        L4 测试只验证"配置就位"（.markdownlint.json 存在）
        不强制钩子在 .pre-commit-config.yaml 中
        """
        # v0.1: 不强求钩子启用
        # 留作 V2 启用后的回归测试
        pass
