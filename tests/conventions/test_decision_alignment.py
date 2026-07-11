"""L4 规范测试 — 关键决策未对齐拦开工（V2.3 #50）

对照 scripts/check_decision_alignment.py：提案契约（Owner 决策节）+ 待拍板检测
+ 新交付识别 + skip + 全仓审计 + 交流 agent 定义存在。
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_decision_alignment.py"
AGENT = REPO_ROOT / ".claude" / "agents" / "liaison.md"


def _load():
    spec = importlib.util.spec_from_file_location("check_decision_alignment", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAgentDefinition:
    def test_liaison_agent_exists_with_contract(self):
        assert AGENT.exists(), "交流 agent 定义缺失（.claude/agents/liaison.md）"
        text = AGENT.read_text(encoding="utf-8")
        for kw in ("需求对齐", "决策", "拍板", "AskUserQuestion"):
            assert kw in text, f"交流 agent 定义缺关键约定: {kw}"
        assert "name: liaison" in text


class TestProposalContract:
    def test_missing_decision_section_fails(self):
        mod = _load()
        errs, _ = mod.check_proposal(
            "docs/plan/design/设计提案-x.md", "# 提案\n## 一、背景\n"
        )
        assert errs and "Owner 决策" in errs[0]

    def test_decision_section_passes(self):
        mod = _load()
        errs, pending = mod.check_proposal(
            "docs/plan/design/设计提案-x.md",
            "# 提案\n## 六、Owner 决策（已锁定）\n| 1 | x | A | A | 已拍板 |\n",
        )
        assert errs == [] and pending is False

    def test_pending_detected(self):
        mod = _load()
        _, pending = mod.check_proposal(
            "docs/plan/design/设计提案-x.md",
            "## Owner 决策\n| 1 | x | A/B | - | 待拍板 |\n",
        )
        assert pending is True


class TestDoneFps:
    def test_done_set_diff(self):
        mod = _load()
        head = "| 49 | a | ⏳ |\n| 50 | b | ⏳ |\n"
        staged = "| 49 | a | ⏳ |\n| 50 | b | ✅ 已完成 |\n"
        assert mod.done_fps(staged) - mod.done_fps(head) == {50}


class TestHook:
    def test_skip_align_passes(self, tmp_path):
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: x [skip-align]", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"[skip-align] 应放行：\n{r.stdout}\n{r.stderr}"

    def test_audit_all_passes_repo(self):
        """全仓提案审计：既有提案都有 Owner 决策节"""
        r = subprocess.run(
            [sys.executable, str(CHECKER), "--all"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        assert r.returncode == 0, f"--all 审计失败：\n{r.stdout}\n{r.stderr}"
