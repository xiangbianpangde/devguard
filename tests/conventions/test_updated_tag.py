"""L4 规范测试 — 「更新时间」标签强制化（V2.3 #53 + #54 全仓泛化）

对照 scripts/check_updated_tag.py：
- 受管范围（全仓文档 .md 减排除项）判定正确
- 所有在范围 .md 都已携带「更新」标签
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_updated_tag.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_updated_tag", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tracked_md() -> list[str]:
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "*.md"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
        check=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


class TestScopeLogic:
    def test_in_scope_includes_docs(self):
        mod = _load_checker()
        for rel in (
            "STATUS.md",
            "CLAUDE.md",
            "conventions/01-architecture_架构设计规范.md",
            "docs/specs/01-architecture.md",
        ):
            assert mod.in_scope(rel), f"{rel} 应在受管范围"

    def test_in_scope_excludes_templates_worklogs_changelog_github(self):
        mod = _load_checker()
        for rel in (
            "docs/templates/worklog模板.md",
            "worklogs/2026-06-11_x.md",
            "CHANGELOG.md",
            ".github/pull_request_template.md",
            "scripts/x.py",
        ):
            assert not mod.in_scope(rel), f"{rel} 不应在受管范围"


class TestAllInScopeTagged:
    def test_every_in_scope_md_has_update_tag(self):
        """全仓在范围 .md 必须都已携带「更新」标签（#54 回填后的不变量）。"""
        mod = _load_checker()
        missing = []
        for rel in _tracked_md():
            if not mod.in_scope(rel):
                continue
            content = (REPO_ROOT / rel).read_text(encoding="utf-8")
            if mod.extract_update_date(content) is None:
                missing.append(rel)
        assert (
            not missing
        ), f"{len(missing)} 个在范围 .md 缺「更新」标签: {missing[:10]}"


class TestCheckerLogic:
    def test_extract_update_date(self):
        mod = _load_checker()
        assert mod.extract_update_date("# t\n> 更新: 2026-06-11（x）\n") == "2026-06-11"
        assert mod.extract_update_date("> 更新：2026-01-02") == "2026-01-02"  # 全角冒号
        assert mod.extract_update_date("# 无标签\n正文") is None

    def test_skip_marker_passes(self, tmp_path):
        """commit message 含 [skip-updated] → 返回 0（不论 staged 状态）。"""
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("docs: 纯格式回滚 [skip-updated]", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"[skip-updated] 应放行：\n{r.stdout}\n{r.stderr}"
