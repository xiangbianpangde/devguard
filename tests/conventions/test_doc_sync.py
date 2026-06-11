"""L4 规范测试 — 四件套文档硬同步（V2.3 阶段C 补遗，#52 拆出项）

对照 scripts/check_doc_sync.py：编号行提取 + 增量同步判定（分粒度：结构硬拦/值级 warn）+ skip。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_doc_sync.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_doc_sync", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestExtract:
    def test_status_fp_rows(self):
        mod = _load()
        text = (
            "| #47 ai-workflow 重映射 | - | ✅ | 2026-06-11 |\n"
            "| **#48 模板族** | - | ✅ | x |\n"
            "| 架构设计规范 (01) | specs | ✅ | - |\n"  # 无编号历史行不参与
            "| v0.1 | 2026-05-27 | #29-#31 |\n"  # 收束历史行首格非 #N
        )
        assert mod.status_fps(text) == {47, 48}

    def test_plan_fp_rows(self):
        mod = _load()
        text = "| 49 | **脚手架** | - | ⏳ |\n| 50 | agent | - | ✅ |\n|---|---|\n"
        assert mod.plan_fps(text) == {49, 50}


class TestSyncRules:
    def test_added_in_status_missing_in_plan_fails(self):
        mod = _load()
        errors, structural = mod.sync_errors(
            {47}, {47, 55}, {47}, {47}, claude_staged=True
        )
        assert structural and any("开发清单（暂存后）没有" in e for e in errors)

    def test_added_both_sides_with_claude_passes(self):
        mod = _load()
        errors, structural = mod.sync_errors(
            {47}, {47, 55}, {47}, {47, 55}, claude_staged=True
        )
        assert structural and errors == []

    def test_structural_without_claude_fails(self):
        mod = _load()
        errors, _ = mod.sync_errors({47}, {47, 55}, {47}, {47, 55}, claude_staged=False)
        assert any("CLAUDE.md 未同提交" in e for e in errors)

    def test_value_only_change_no_errors(self):
        """行集不变（仅状态/日期值变）→ 非结构性、零 error（分粒度）"""
        mod = _load()
        errors, structural = mod.sync_errors(
            {47, 48}, {47, 48}, {47, 48}, {47, 48}, claude_staged=False
        )
        assert errors == [] and structural is False

    def test_removed_in_status_lingering_in_plan_fails(self):
        mod = _load()
        errors, _ = mod.sync_errors(
            {47, 55}, {47}, {47, 55}, {47, 55}, claude_staged=True
        )
        assert any("仍保留" in e for e in errors)


class TestHook:
    def test_skip_docsync_passes(self, tmp_path):
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: x [skip-docsync]", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"[skip-docsync] 应放行：\n{r.stdout}\n{r.stderr}"
