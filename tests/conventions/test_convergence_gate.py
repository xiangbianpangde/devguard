"""L4 规范测试 — 收束硬闸门（V2.3 #52，节点驱动版）

对照 scripts/check_convergence_gate.py：标记解析（预设节点 + 已收束）+ 最大完成编号 + 闸门标记存在。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS = REPO_ROOT / "STATUS.md"
CHECKER = REPO_ROOT / "scripts" / "check_convergence_gate.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_convergence_gate", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestMarker:
    def test_status_has_gate_marker(self):
        mod = _load()
        parsed = mod.parse_marker(STATUS.read_text(encoding="utf-8"))
        assert parsed is not None, "STATUS.md 缺 convergence-gate 标记"
        nodes, last_fp = parsed
        assert nodes, "预设节点列表不应为空"
        assert last_fp >= 0

    def test_parse_marker(self):
        mod = _load()
        marker = "x <!-- convergence-gate: nodes=46,54 last_converged_fp=46 -->"
        assert mod.parse_marker(marker) == ([46, 54], 46)
        assert mod.parse_marker("no marker here") is None


class TestMaxDoneFp:
    def test_picks_highest_done(self):
        mod = _load()
        plan = (
            "| # | 功能点 | 状态 |\n"
            "|---|------|------|\n"
            "| 46 | a | ✅ 已完成 |\n"
            "| 47 | b | ⏳ 待开始 |\n"  # 未完成，不计
            "| 54 | c | ✅ 已完成 |\n"
        )
        assert mod.max_done_fp(plan) == 54

    def test_no_done_is_zero(self):
        mod = _load()
        assert mod.max_done_fp("| 99 | x | ⏳ |\n") == 0


class TestSkip:
    def test_skip_gate_passes(self, tmp_path):
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: x [skip-gate]", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"[skip-gate] 应放行：\n{r.stdout}\n{r.stderr}"
