"""check_ai_workflow 与 check_coverage_matrix 的契约测试（R5-22 补覆盖）。"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _load(script: str):
    spec = importlib.util.spec_from_file_location(
        script.removesuffix(".py"), REPO_ROOT / "scripts" / script
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestAiWorkflow:
    def test_all_nine_documents_pass(self):
        r = _run("check_ai_workflow.py")
        assert r.returncode == 0, r.stdout + r.stderr

    def test_empty_shell_document_fails(self, tmp_path, monkeypatch):
        """R5-14：5 行空壳（含 1 个关键词）必须被拦截。"""
        mod = _load("check_ai_workflow.py")
        shell_dir = tmp_path / "flow"
        shell_dir.mkdir()
        (shell_dir / "09-部署规范.md").write_text("# x\n\n## 一\n\n部署\n", encoding="utf-8")
        monkeypatch.setattr(mod, "WORKFLOW_DIR", shell_dir)
        assert mod.main() != 0  # 空壳：全文缺关键词 → FAIL


class TestCoverageMatrix:
    def test_passes_on_repository(self):
        r = _run("check_coverage_matrix.py")
        assert r.returncode == 0, r.stdout + r.stderr

    def test_mutation_of_spec_row_fails(self, tmp_path, monkeypatch):
        """变异：矩阵规范行编号改错 → FAIL（C1 关键闸门有效性）。"""
        mod = _load("check_coverage_matrix.py")
        matrix = REPO_ROOT / mod.MATRIX_REL
        original = matrix.read_text(encoding="utf-8")
        try:
            mutated = original.replace("| 01 | 架构设计 |", "| 16 | 架构设计 |", 1)
            assert mutated != original
            matrix.write_text(mutated, encoding="utf-8")
            r = _run("check_coverage_matrix.py")
            assert r.returncode != 0, "变异后必须 FAIL"
            assert "缺规范行" in r.stderr
        finally:
            matrix.write_text(original, encoding="utf-8")
