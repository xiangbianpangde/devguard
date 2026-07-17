"""L4 规范测试 — 02-coding

对照 conventions/02-coding_代码编写规范.md §一 红线 1-7：
1. 禁 print / console.log → ruff T20
2. SQL 必须参数化 → ruff S608 (bandit)
3. 密钥 / Token 禁硬编码 → ruff S105-S107 + gitleaks
4. 禁静默吞异常（except: pass / catch {}）→ ruff E722 S110
5. 禁提交注释掉的代码、调试断点 → ruff T100 + 审查
6. 日志禁输出敏感信息 → 审查（无可靠自动规则）
7. 外部输入必须校验后再使用 → 审查 + 类型校验库
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUFF_TOML = REPO_ROOT / "src" / "coding" / "ruff.toml"
PRE_COMMIT_YAML = REPO_ROOT / ".pre-commit-config.yaml"
CONV_02 = REPO_ROOT / "conventions" / "02-coding_代码编写规范.md"


def _read_toml_select(path: Path) -> list[str]:
    """从 ruff.toml 提取 [lint] select 列表（粗解析，不引入 tomli）"""
    content = path.read_text(encoding="utf-8")
    m = re.search(r"^\s*select\s*=\s*\[(.*?)\]", content, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    raw = m.group(1)
    return [s.strip().strip('"').strip("'") for s in raw.split(",") if s.strip()]


class TestCodingContracts:
    """02-coding §一 红线 1-7 的 L4 检测"""

    def test_ruff_config_exists(self):
        """L1 检测工具 ruff.toml 必须存在（红线 1/2/4/5 的载体）"""
        assert RUFF_TOML.exists(), f"ruff.toml 缺失（{RUFF_TOML}）"

    def test_ruff_selects_required_rules(self):
        """红线 1/2/4/5 需要的 ruff 规则必须在 select 中：T20 / S / E / T100"""
        rules = _read_toml_select(RUFF_TOML)
        required = {"T20", "S", "E", "T100"}
        missing = required - set(rules)
        assert not missing, f"ruff.toml select 缺红线规则：{missing}"

    def test_ruff_check_runs_clean_on_src_coding(self):
        """红线 1-5 的 ruff 检查在 src/coding/ 跑通（含教学反例豁免）"""
        result = subprocess.run(
            [
                "ruff",
                "check",
                "src/coding/",
                "--config",
                str(RUFF_TOML),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, (
            f"ruff check src/coding/ 失败（红线 1-5 检测）：\n{result.stdout}\n{result.stderr}"
        )

    def test_gitleaks_in_precommit(self):
        """红线 3：gitleaks 必须在 .pre-commit-config.yaml 中（密钥扫描）"""
        assert PRE_COMMIT_YAML.exists()
        content = PRE_COMMIT_YAML.read_text(encoding="utf-8")
        assert "gitleaks" in content, (
            "pre-commit-config.yaml 缺 gitleaks 钩子（红线 3 密钥扫描无自动检测）"
        )

    def test_redline_6_in_checklist(self):
        """红线 6（日志脱敏）是审查项，必须在 02 §六 检查清单里有对应项"""
        assert CONV_02.exists()
        content = CONV_02.read_text(encoding="utf-8")
        # §六 检查清单应该提到 "日志不含敏感"
        assert "日志" in content and "敏感" in content, (
            "02 §六 检查清单缺日志脱敏项（红线 6：日志禁输出敏感信息）"
        )

    def test_redline_7_in_checklist(self):
        """红线 7（外部输入校验）是审查项，必须在 02 §六 检查清单里有对应项"""
        content = CONV_02.read_text(encoding="utf-8")
        assert "外部输入" in content and "校验" in content, (
            "02 §六 检查清单缺输入校验项（红线 7：所有外部输入必须校验）"
        )

    def test_demo_files_excluded(self):
        """教学反例豁免规则存在（确认 02 红线对教学反例的合理豁免）"""
        content = RUFF_TOML.read_text(encoding="utf-8")
        assert "src/**/*.py" in content, (
            "ruff.toml 缺 src/ 整体豁免规则（教学代码需合理豁免 print 等红线）"
        )
