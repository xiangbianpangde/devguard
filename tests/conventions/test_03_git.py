"""L4 规范测试 — 03-git

对照 conventions/03-git_Git协作规范.md §一 红线 1-5：
1. main 禁直推 → 平台分支保护（不可本地测，断言有相关文档）
2. 提交符合 Conventional Commits → commitlint + commit-msg hook
3. 一个 commit 只做一件事 → 审查 + commitlint
4. 禁 force push 共享分支 → 平台分支保护
5. 合入需 1 人 Approve → 平台分支保护

红线 1/4/5 是平台分支保护，本地无法验证；L4 测试断言"配置存在 + 文档覆盖"。
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT_YAML = REPO_ROOT / ".pre-commit-config.yaml"
COMMITLINT_CONFIG = REPO_ROOT / "commitlint.config.js"
CONV_03 = REPO_ROOT / "conventions" / "03-git_Git协作规范.md"
GITMESSAGE = REPO_ROOT / ".gitmessage"
PR_TEMPLATE = REPO_ROOT / ".github" / "pull_request_template.md"


class TestGitContracts:
    """03-git §一 红线 1-5 的 L4 检测"""

    def test_commitlint_config_exists(self):
        """红线 2/3：commitlint.config.js 必须存在"""
        assert (
            COMMITLINT_CONFIG.exists()
        ), f"commitlint.config.js 缺失（{COMMITLINT_CONFIG}）—— 提交格式无自动校验"

    def test_commitlint_in_precommit(self):
        """红线 2：commitlint v0.1 暂不启用（V2 加 package.json 后启用）

        v0.1: 项目无 npm 依赖，commitlint 钩子不挂；配置留在 commitlint.config.js
        L4 测试只验证"配置就位 + 钩子或 worklog 引用存在"
        """
        content = PRE_COMMIT_YAML.read_text(encoding="utf-8")
        assert (
            "worklog" in content or "commitlint" in content
        ), "pre-commit-config.yaml 应该含 worklog 引用钩子（红线 6）或 commitlint（红线 2）"

    def test_commitlint_extends_conventional(self):
        """红线 2：commitlint.config.js 必须 extends @commitlint/config-conventional（配置就位）"""
        content = COMMITLINT_CONFIG.read_text(encoding="utf-8")
        assert (
            "config-conventional" in content
        ), "commitlint.config.js 必须 extends @commitlint/config-conventional"

    def test_commitlint_includes_recommended_types(self):
        """红线 3：commitlint 必须包含 03 §三 推荐 type（feat/fix/refactor/docs/test/perf/style/chore）"""  # noqa: E501
        content = COMMITLINT_CONFIG.read_text(encoding="utf-8")
        # 检查 type-enum 包含至少 5 个标准 type
        for t in ["feat", "fix", "refactor", "docs", "test", "chore"]:
            assert (
                f"'{t}'" in content or f'"{t}"' in content
            ), f"commitlint type-enum 缺 {t}（03 §三 推荐 type 列表）"

    def test_gitmessage_template_exists(self):
        """03 §二：.gitmessage 提交模板应存在（指导 commit 写法）"""
        assert GITMESSAGE.exists(), ".gitmessage 提交模板缺失——开发者提交时无格式引导"

    def test_pr_template_exists(self):
        """03 §二：.github/pull_request_template.md 应存在（PR 描述引导）"""
        assert (
            PR_TEMPLATE.exists()
        ), ".github/pull_request_template.md 缺失——PR 描述无引导"

    def test_branch_protection_documented(self):
        """红线 1/4/5（平台分支保护）必须在 03 §二 落地有文档指引"""
        content = CONV_03.read_text(encoding="utf-8")
        # §二 落地应该提到 "分支保护" 或 "branch protection"
        assert (
            "分支保护" in content
        ), "03 §二 落地缺分支保护设置指引（红线 1/4/5 无落地说明）"
