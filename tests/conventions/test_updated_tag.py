"""L4 规范测试 — 「更新时间」标签强制化（V2.3 #53）

对照 scripts/check_updated_tag.py：受管文件均携带「更新」标签 + 钩子逻辑正确。
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


class TestManagedFilesTagged:
    def test_all_managed_files_exist(self):
        mod = _load_checker()
        for rel in mod.MANAGED:
            assert (REPO_ROOT / rel).exists(), f"受管文件不存在: {rel}"

    def test_all_managed_files_have_update_tag(self):
        """每个受管文件都必须携带 `> 更新: YYYY-MM-DD` 标签。"""
        mod = _load_checker()
        for rel in mod.MANAGED:
            content = (REPO_ROOT / rel).read_text(encoding="utf-8")
            date = mod.extract_update_date(content)
            assert date is not None, f"{rel} 缺「更新」标签"


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
