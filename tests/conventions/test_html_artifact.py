"""L4 规范测试 — HTML 产出物结构校验（V2.3 #48）

对照 scripts/check_html_artifact.py：模板族自检 + 契约缺章节检测 + untyped 软提示 + skip。
"""

from __future__ import annotations

import importlib.util
import os
import subprocess

import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_html_artifact.py"
TEMPLATES = REPO_ROOT / "docs" / "templates"

FAMILY = {
    "汇报模板.html": "report",
    "计划模板.html": "plan",
    "实施设计模板.html": "impl-design",
    "绘图素材库模板.html": "asset-library",
}


def _load():
    spec = importlib.util.spec_from_file_location("check_html_artifact", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTemplateFamily:
    def test_four_templates_exist_and_typed(self):
        mod = _load()
        for name, expected_type in FAMILY.items():
            fp = TEMPLATES / name
            assert fp.exists(), f"模板族缺 {name}"
            m = mod.META_TYPE.search(fp.read_text(encoding="utf-8"))
            assert m and m.group(1) == expected_type, f"{name} 类型声明应为 {expected_type}"

    def test_templates_pass_own_contract(self):
        """模板族每个文件必须通过自身契约（自举：模板违约即坏）"""
        mod = _load()
        for name in FAMILY:
            rel = f"docs/templates/{name}"
            content = (TEMPLATES / name).read_text(encoding="utf-8")
            errors, _ = mod.check_content(rel, content)
            assert errors == [], f"{name} 违反自身契约: {errors}"


class TestContract:
    def test_missing_sections_fail(self):
        mod = _load()
        html = (
            '<!DOCTYPE html><html><head><meta name="doc-template" content="report">'
            "<title>t</title></head><body><nav></nav>"
            '<section id="sec-evidence"></section></body></html>'
        )
        errors, _ = mod.check_content("docs/reports/x.html", html)
        assert any("缺必备章节" in e for e in errors), f"应报缺章节: {errors}"

    def test_unknown_type_fails(self):
        mod = _load()
        html = '<meta name="doc-template" content="nonsense">'
        errors, _ = mod.check_content("docs/reports/x.html", html)
        assert any("未知" in e for e in errors)

    def test_untyped_artifact_warn_only(self):
        """存量/未声明类型的产出物：仅 WARN 不拦（分粒度原则）"""
        mod = _load()
        errors, warnings = mod.check_content(
            "docs/reports/legacy.html", "<!DOCTYPE html><html></html>"
        )
        assert errors == []
        assert any("doc-template" in w for w in warnings)

    def test_untyped_template_silent(self):
        """docs/templates/ 下未声明类型的 html（dashboard 渲染模板等）不打扰"""
        mod = _load()
        errors, warnings = mod.check_content(
            "docs/templates/devguard/final-report-template/template.html",
            "<!DOCTYPE html><html></html>",
        )
        assert errors == [] and warnings == []


class TestHook:
    def test_skip_html_passes(self, tmp_path):
        msg = tmp_path / "COMMIT_EDITMSG"
        msg.write_text("feat: x [skip-html]", encoding="utf-8")
        r = subprocess.run([sys.executable, str(CHECKER), str(msg)], capture_output=True, text=True)
        assert r.returncode == 0, f"[skip-html] 应放行：\n{r.stdout}\n{r.stderr}"

    def test_audit_all_passes_repo(self):
        """--all 全仓审计：typed 文件（模板族）零违规"""
        r = subprocess.run(
            [sys.executable, str(CHECKER), "--all"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        assert r.returncode == 0, f"--all 审计失败：\n{r.stdout}\n{r.stderr}"


FINAL_REPORT_CANONICAL = [
    "docs/templates/devguard/final-report-template/template.html",
    "docs/templates/devguard/final-report-template/demo.html",
    "docs/reports/2026-06-08_devguard_V1.5_V2.0_merged_report.html",
    "docs/reports/2026-07-17_devguard_审查修复_验收报告.html",
]


def _final_report_html(*, mermaid: int = 2, drop: tuple[str, ...] = ()) -> str:
    anchors = {
        "hero": '<section class="hero"></section>',
        "kpi-row": '<div class="kpi-row"></div>',
        "toc": '<div class="toc"></div>',
        "verdict": '<div class="verdict"></div>',
    }
    body = [
        '<!DOCTYPE html><html><head><meta name="doc-template" content="final-report">',
        "<title>t</title></head><body><nav></nav>",
    ]
    body.extend(html for name, html in anchors.items() if name not in drop)
    body.extend(['<div class="mermaid"></div>'] * mermaid)
    body.append("</body></html>")
    return "".join(body)


class TestFinalReportContract:
    """V2.4 #53：final-report 类型契约（hero / kpi-row / TOC / ≥2 mermaid / verdict）"""

    def test_contract_registered(self):
        mod = _load()
        assert "final-report" in mod.CLASS_CONTRACTS

    @pytest.mark.parametrize("rel", FINAL_REPORT_CANONICAL)
    def test_canonical_files_satisfy_anchors(self, rel):
        """4 份 canonical（模板/demo/merged_report/2026-07-17 验收报告）必须全部满足锚点"""
        mod = _load()
        content = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert mod.final_report_anchor_errors(content) == [], f"{rel} 锚点缺失"

    def test_typed_files_pass_whole_check(self):
        """打标后的 template/demo/验收报告通过完整校验（untyped merged_report 留给 #54）"""
        mod = _load()
        for rel in FINAL_REPORT_CANONICAL:
            if "merged_report" in rel:
                continue
            errors, _ = mod.check_content(rel, (REPO_ROOT / rel).read_text(encoding="utf-8"))
            assert errors == [], f"{rel} 完整校验失败: {errors}"

    def test_missing_class_anchor_fails(self):
        mod = _load()
        for drop in (("verdict",), ("kpi-row",), ("hero",), ("toc",)):
            errors, _ = mod.check_content("docs/reports/x.html", _final_report_html(drop=drop))
            assert any("缺必备锚点" in e for e in errors), f"缺 {drop} 应 FAIL: {errors}"

    def test_single_mermaid_fails_two_passes(self):
        """mermaid 计数边界：1 个 fail，2 个 pass"""
        mod = _load()
        errors, _ = mod.check_content("docs/reports/x.html", _final_report_html(mermaid=1))
        assert any("mermaid" in e for e in errors), f"1 个 mermaid 应 FAIL: {errors}"
        errors, _ = mod.check_content("docs/reports/x.html", _final_report_html(mermaid=2))
        assert errors == [], f"2 个 mermaid 应通过: {errors}"

    def test_untyped_final_report_style_still_warn_only(self):
        """高密度风但未声明类型的存量（如 merged_report）：仅 WARN 不拦"""
        mod = _load()
        content = _final_report_html().replace(
            '<meta name="doc-template" content="final-report">', ""
        )
        errors, warnings = mod.check_content("docs/reports/legacy.html", content)
        assert errors == []
        assert any("doc-template" in w for w in warnings)
