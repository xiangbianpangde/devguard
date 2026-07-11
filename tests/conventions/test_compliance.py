"""Compliance checks must reject empty or malformed evidence."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "scripts" / "check_compliance.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_compliance", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_empty_file_is_not_compliant(tmp_path):
    module = _load()
    artifact = tmp_path / "empty.yaml"
    artifact.write_text("", encoding="utf-8")

    passed, detail = module.validate_artifact(artifact)

    assert not passed
    assert "空" in detail


def test_malformed_yaml_is_not_compliant(tmp_path):
    module = _load()
    artifact = tmp_path / "broken.yaml"
    artifact.write_text("key: [unterminated\n", encoding="utf-8")

    passed, detail = module.validate_artifact(artifact)

    assert not passed
    assert "解析失败" in detail


def test_python_must_compile(tmp_path):
    module = _load()
    artifact = tmp_path / "broken.py"
    artifact.write_text("def broken(:\n", encoding="utf-8")

    passed, detail = module.validate_artifact(artifact)

    assert not passed
    assert "解析失败" in detail


def test_l4_file_requires_real_test_definition(tmp_path):
    module = _load()
    artifact = tmp_path / "test_claim.py"
    artifact.write_text("VALUE = 'test_only_in_text'\n", encoding="utf-8")

    passed, detail = module.contains_test_contract(artifact)

    assert not passed
    assert "test_" in detail
