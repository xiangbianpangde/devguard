"""L4 规范测试 — 基准约束脚手架（V2.3 #49）

对照 scripts/setup_scaffold.py：清单完整性 + 两层复制 + _meta 钩子节拼接 + 目标可渲染。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = REPO_ROOT / "scripts" / "setup_scaffold.py"


def _load():
    spec = importlib.util.spec_from_file_location("setup_scaffold", SCAFFOLD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestManifest:
    def test_all_sources_exist(self):
        """清单源文件必须全部存在——脚手架与仓库不脱钩"""
        mod = _load()
        missing = [
            src
            for src, _ in mod.CORE_MANIFEST + mod.OPTIONAL_MANIFEST
            if not (REPO_ROOT / src).exists()
        ]
        assert missing == [], f"脚手架清单源缺失: {missing}"


class TestSetup:
    def test_core_layer(self, tmp_path):
        mod = _load()
        target = tmp_path / "newproj"
        mod.setup(target, with_optional=False, force=False)
        for rel in (
            "conventions/_meta.yaml",
            "scripts/render_meta.py",
            "scripts/check_doc_sync.py",
            ".github/workflows/ci.yml",
            "commitlint.config.js",
            "meta/豁免清单.md",
            "docs/templates/CLAUDE模板.md",
        ):
            assert (target / rel).exists(), f"必带层缺 {rel}"
        meta = (target / "conventions/_meta.yaml").read_text(encoding="utf-8")
        assert "commit-msg-doc-sync" in meta, "必带层 _meta 应含核心钩子"
        assert "commit-msg-convergence-gate" not in meta, "必带层不应含可选钩子"
        assert not (target / "scripts/check_convergence_gate.py").exists()
        reg = (target / "meta/豁免清单.md").read_text(encoding="utf-8")
        assert "[skip-docsync]" in reg and "[skip-gate]" not in reg

    def test_optional_layer(self, tmp_path):
        mod = _load()
        target = tmp_path / "newproj2"
        mod.setup(target, with_optional=True, force=False)
        for rel in (
            "scripts/check_convergence_gate.py",
            ".claude/agents/liaison.md",
            "docs/templates/汇报模板.html",
        ):
            assert (target / rel).exists(), f"可选层缺 {rel}"
        meta = (target / "conventions/_meta.yaml").read_text(encoding="utf-8")
        assert "commit-msg-convergence-gate" in meta
        reg = (target / "meta/豁免清单.md").read_text(encoding="utf-8")
        assert "[skip-gate]" in reg

    def test_refuse_nonempty_without_force(self, tmp_path):
        mod = _load()
        target = tmp_path / "occupied"
        target.mkdir()
        (target / "x.txt").write_text("x", encoding="utf-8")
        try:
            mod.setup(target, with_optional=False, force=False)
            raise AssertionError("非空目录无 --force 应拒绝")
        except SystemExit:
            pass

    def test_target_renders_pre_commit_config(self, tmp_path):
        """E2E：脚手架目标里 render_meta 可直接渲染出 .pre-commit-config.yaml"""
        mod = _load()
        target = tmp_path / "newproj3"
        mod.setup(target, with_optional=False, force=False)
        r = subprocess.run(
            [sys.executable, "scripts/render_meta.py", "--render", "pre-commit-config"],
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        cfg = target / ".pre-commit-config.yaml"
        assert r.returncode == 0 and cfg.exists(), f"渲染失败:\n{r.stdout}\n{r.stderr}"
        text = cfg.read_text(encoding="utf-8")
        assert "check_doc_sync.py" in text and "check_worklog_ref.py" in text
        assert "check_convergence_gate.py" not in text
