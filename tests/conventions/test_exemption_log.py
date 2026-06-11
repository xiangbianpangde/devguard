"""L4 规范测试 — 豁免登记强制化（V2.3 #51）

对照 scripts/check_exemption_log.py + meta/豁免清单.md：
验证豁免账结构完整 + 钩子判定逻辑正确。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "meta" / "豁免清单.md"
CHECKER = REPO_ROOT / "scripts" / "check_exemption_log.py"


def _load_checker():
    """动态导入 check_exemption_log 以测纯函数。"""
    spec = importlib.util.spec_from_file_location("check_exemption_log", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRegistryStructure:
    def test_registry_exists(self):
        assert REGISTRY.exists(), "meta/豁免清单.md 不存在"

    def test_registry_has_catalog_section(self):
        content = REGISTRY.read_text(encoding="utf-8")
        assert "## 二、已登记豁免标记" in content, "缺 §二 已登记豁免标记目录"

    def test_registry_has_usage_log_section(self):
        content = REGISTRY.read_text(encoding="utf-8")
        assert "## 三、豁免使用记录" in content, "缺 §三 豁免使用记录"

    def test_registry_documents_existing_markers(self):
        """现役 4 个豁免标记必须都在清单登记。"""
        mod = _load_checker()
        registered = mod.registry_markers()
        for marker in (
            "[skip-worklog]",
            "[skip-status]",
            "[skip-worklog-structure]",
            "[skip-file-placement]",
        ):
            assert marker in registered, f"{marker} 未在豁免清单登记"


class TestCheckerLogic:
    def test_extract_skip_markers(self):
        mod = _load_checker()
        assert mod.extract_skip_markers("feat: x") == set()
        assert mod.extract_skip_markers("fix: y [skip-worklog]") == {"[skip-worklog]"}
        got = mod.extract_skip_markers("a [skip-worklog] b [skip-status]")
        assert got == {"[skip-worklog]", "[skip-status]"}
        # [meta] 不是 [skip-*]，不应被当作豁免标记
        assert mod.extract_skip_markers("chore: bump [meta]") == set()

    def test_no_marker_passes(self, tmp_path):
        """无豁免标记的 commit message → 返回 0。"""
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text(
            "feat(x): 实现功能（详见 worklogs/2026-06-11_x.md）", encoding="utf-8"
        )
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"无标记却被拦：\n{r.stdout}\n{r.stderr}"

    def test_unregistered_marker_fails(self, tmp_path):
        """使用未登记的豁免标记 → 返回 1（不依赖 git staging 状态）。"""
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("fix: y [skip-nonexistent-xyz]", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 1, "未登记标记应被拦截"
        assert "未登记" in (r.stdout + r.stderr)
