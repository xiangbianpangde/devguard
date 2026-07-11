"""L4 规范测试 — STATUS.md 章节级 L1（V2.1 #40）

对照 scripts/check_status.py：验证 STATUS.md 结构完整。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS = REPO_ROOT / "STATUS.md"
CHECKER = REPO_ROOT / "scripts" / "check_status.py"


class TestStatusStructure:
    def test_checker_passes(self):
        """check_status.py 对真实 STATUS.md 返回 0"""
        r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
        assert r.returncode == 0, f"check_status 失败:\n{r.stdout}\n{r.stderr}"

    def test_has_progress_section(self):
        content = STATUS.read_text(encoding="utf-8")
        assert "## 当前进度" in content, "STATUS.md 缺 ## 当前进度 节"

    def test_has_convergence_history_section(self):
        content = STATUS.read_text(encoding="utf-8")
        assert "## 收束节点历史" in content, "STATUS.md 缺 ## 收束节点历史 节"

    def test_convergence_table_has_9_columns(self):
        """收束节点历史表列数 ≥ 9"""
        lines = STATUS.read_text(encoding="utf-8").splitlines()
        in_section = False
        header_cols = 0
        for line in lines:
            if line.startswith("## "):
                in_section = "收束节点历史" in line
                continue
            if in_section and line.strip().startswith("|"):
                header_cols = len([c for c in line.strip().strip("|").split("|")])
                break
        assert header_cols >= 9, f"收束节点历史表列数 {header_cols} < 9"
