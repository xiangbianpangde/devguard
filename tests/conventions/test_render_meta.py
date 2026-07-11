"""Focused contracts for metadata rendering."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_render_meta():
    spec = importlib.util.spec_from_file_location(
        "render_meta_under_test", REPO_ROOT / "scripts" / "render_meta.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _markdown_convention(file_name: str) -> dict:
    return {
        "file": file_name,
        "grade": {"red_line": 1, "warning": 0, "recommend": 0},
        "l1_check": "pytest",
        "l3_route": "task=test",
    }


def test_rendered_pre_commit_is_canonical_lf_with_one_terminal_newline():
    render_meta = _load_render_meta()

    rendered = render_meta.render_pre_commit_config(
        {
            "pre_commit": [
                {
                    "id": "check-yaml",
                    "source": "pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                }
            ]
        }
    )

    assert "\r" not in rendered
    assert rendered.endswith("\n")
    assert not rendered.endswith("\n\n")


def test_convention_grade_renders_only_markdown_and_writes_canonical_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    render_meta = _load_render_meta()
    markdown = tmp_path / "rule.md"
    native = tmp_path / "CODEOWNERS"
    markdown.write_bytes(b"# Rule\r\n\r\nBody\r\n\r\n")
    native.write_text("* @owner\n", encoding="utf-8")
    monkeypatch.setattr(render_meta, "REPO_ROOT", tmp_path)

    written = render_meta.render_convention_grade(
        {
            "conventions": [
                _markdown_convention(markdown.name),
                _markdown_convention(native.name),
            ]
        }
    )

    assert written == [markdown]
    rendered = markdown.read_bytes()
    assert b"\r" not in rendered
    assert rendered.endswith(b"\n")
    assert not rendered.endswith(b"\n\n")
    assert native.read_text(encoding="utf-8") == "* @owner\n"
    assert render_meta.check_target(
        "convention-grade",
        {
            "conventions": [
                _markdown_convention(markdown.name),
                _markdown_convention(native.name),
            ]
        },
    )[0]

    markdown.write_bytes(rendered.replace(b"\n", b"\r\n"))
    assert not render_meta.check_target(
        "convention-grade", {"conventions": [_markdown_convention(markdown.name)]}
    )[0]


@pytest.mark.parametrize("relative_path", [".github/CODEOWNERS", "LICENSE"])
def test_native_repository_files_do_not_contain_markdown_grade(relative_path: str):
    content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    assert "## 分级标签" not in content
