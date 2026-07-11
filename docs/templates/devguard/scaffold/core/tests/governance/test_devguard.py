"""Minimum executable contract for the generated governance baseline."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "devguard.py"


def load_devguard():
    spec = importlib.util.spec_from_file_location("devguard", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_generated_project_is_structurally_closed():
    module = load_devguard()
    assert module.verify(ROOT) == []


def test_commit_message_gate_accepts_and_rejects_expected_shapes(tmp_path):
    module = load_devguard()
    message = tmp_path / "COMMIT_EDITMSG"
    message.write_text("fix(api): reject invalid ids\n", encoding="utf-8")
    assert module.validate_commit_message(message) == []
    message.write_text("updated files\n", encoding="utf-8")
    assert module.validate_commit_message(message)
