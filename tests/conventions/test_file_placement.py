"""L4 规范测试 — 文件放置（V2.1 #45 强化）

校验 scripts/check_file_placement.py 的 placement_error：
  - 根目录散文件拦
  - 已知顶层区（conventions/ src/ …）自由嵌套放行
  - docs/ 必须落子区，根散文件拦
  - 未知顶层区拦
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_file_placement import placement_error  # noqa: E402


class TestFilePlacement:
    def test_root_whitelist_passes(self):
        assert placement_error("CLAUDE.md") is None
        assert placement_error("README.md") is None
        assert placement_error("STATUS.md") is None
        assert placement_error(".markdownlintignore") is None

    def test_root_stray_blocked(self):
        assert placement_error(".unknownfile") is not None
        assert "根目录" in placement_error(".unknownfile")

    def test_free_top_areas_pass(self):
        # 已知顶层区内任意嵌套都合法
        for p in [
            "conventions/foo.md",
            "conventions/ai-workflow_AI协作开发流程/x.md",
            "src/architecture/domain/order.py",
            "src/coding/sub/deep/file.py",
            "worklogs/2026-06-10_x.md",
            "worklogs/decisions/0001.md",
            "scripts/foo.py",
            "meta/anything.md",
            "tests/foo.py",
            "tests/conventions/foo.py",
            ".github/workflows/foo.yml",
            ".claude/settings.json",
        ]:
            assert placement_error(p) is None, f"应合法: {p}"

    def test_docs_root_stray_blocked(self):
        err = placement_error("docs/重构笔记-重构项目指南.md")
        assert err is not None
        assert "docs/ 根" in err

    def test_docs_subsection_passes(self):
        for p in [
            "docs/plan/背景.md",
            "docs/plan/design/foo.md",
            "docs/reports/x.md",
            "docs/research/foo.md",
            "docs/research/图谱与代码理解工具调研-output/tree/N1-x.md",
            "docs/specs/01-architecture.md",
            "docs/templates/foo.md",
            "docs/templates/devguard/foo.py",
            "docs/历史文件/foo.md",
        ]:
            assert placement_error(p) is None, f"应合法: {p}"

    def test_unknown_top_area_blocked(self):
        err = placement_error("random/foo.md")
        assert err is not None
        assert "未登记" in err

    def test_unknown_docs_subsection_blocked(self):
        err = placement_error("docs/unknown/x.md")
        assert err is not None
        assert "未登记" in err
