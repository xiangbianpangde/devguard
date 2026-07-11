"""L4 规范测试 — 开发清单.md 格式 L1（V2.1 #42）

对照 scripts/check_plan.py：验证 开发清单.md 结构完整。
跨文件计数（开发清单 vs STATUS）按方案为 WARN，不在 L4 硬断言。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN = REPO_ROOT / "docs" / "plan" / "开发清单.md"
CHECKER = REPO_ROOT / "scripts" / "check_plan.py"


class TestPlanStructure:
    def test_checker_passes(self):
        r = subprocess.run(
            [sys.executable, str(CHECKER)], capture_output=True, text=True
        )
        assert r.returncode == 0, f"check_plan 失败:\n{r.stdout}\n{r.stderr}"

    def test_has_feature_list_section(self):
        content = PLAN.read_text(encoding="utf-8")
        assert "## 功能点列表" in content, "开发清单.md 缺 ## 功能点列表 节"

    def test_feature_table_has_7_columns(self):
        lines = PLAN.read_text(encoding="utf-8").splitlines()
        in_section = False
        cols = 0
        for line in lines:
            if line.startswith("## "):
                in_section = "功能点列表" in line
                continue
            if in_section and line.strip().startswith("|"):
                cols = len(line.strip().strip("|").split("|"))
                break
        assert cols >= 7, f"功能点列表表列数 {cols} < 7"
