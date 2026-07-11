"""L4 规范测试 — CLAUDE.md 结构 L1（V2.1 #41）

对照 scripts/check_claude.py：验证 CLAUDE.md 必需章节齐全。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE = REPO_ROOT / "CLAUDE.md"
CHECKER = REPO_ROOT / "scripts" / "check_claude.py"


class TestClaudeStructure:
    def test_checker_passes(self):
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
        assert r.returncode == 0, f"check_claude 失败:\n{r.stdout}\n{r.stderr}"

    def test_required_sections_present(self):
        content = CLAUDE.read_text(encoding="utf-8")
        # 概念 -> 任一关键词命中
        required = {
            "项目概述": ["项目概述"],
            "目录结构": ["目录索引", "目录结构"],
            "红线表": ["红线", "规范速查"],
            "工作流程": ["工作流程"],
            "文件放置": ["文件放置", "FILE_GRAPH"],
            "当前状态": ["当前状态"],
        }
        missing = [c for c, kws in required.items() if not any(k in content for k in kws)]
        assert not missing, f"CLAUDE.md 缺必需章节：{missing}"

    def test_redline_table_has_min_rows(self):
        """红线/规范速查表 ≥ 6 维度行"""
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
        # checker 通过即代表红线表 ≥ 6 行
        assert r.returncode == 0
