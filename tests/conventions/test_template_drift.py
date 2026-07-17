"""模板漂移检测：scripts/ 与 docs/templates/devguard/scripts/ 镜像必须逐字节一致。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_template_drift.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_template_drift", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_shared_scripts_are_byte_identical_in_repository():
    """真实仓库：共有脚本零漂移（render_meta.py / lint_markdown.py 等）"""
    mod = _load()

    assert mod.check_script_mirrors(REPO_ROOT) == []


def test_mirror_mismatch_is_detected(tmp_path: Path):
    """人为制造漂移必须被检出并点名文件"""
    mod = _load()
    _write(tmp_path, "scripts/render_meta.py", "v2\n")
    _write(tmp_path, "docs/templates/devguard/scripts/render_meta.py", "v1\n")

    errors = mod.check_script_mirrors(tmp_path)

    assert len(errors) == 1
    assert "render_meta.py" in errors[0]


def test_template_orphan_script_is_reported(tmp_path: Path):
    """模板里存在而仓里缺失的脚本同样是漂移"""
    mod = _load()
    _write(tmp_path, "docs/templates/devguard/scripts/ghost.py", "x\n")

    errors = mod.check_script_mirrors(tmp_path)

    assert len(errors) == 1
    assert "ghost.py" in errors[0]


def test_identical_mirror_passes(tmp_path: Path):
    mod = _load()
    _write(tmp_path, "scripts/a.py", "same\n")
    _write(tmp_path, "docs/templates/devguard/scripts/a.py", "same\n")

    assert mod.check_script_mirrors(tmp_path) == []
