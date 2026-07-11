"""Scaffold contract tests: deployable payload, safe writes, and fail-closed verify."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_PATH = REPO_ROOT / "scripts" / "setup_scaffold.py"


def load_scaffold():
    spec = importlib.util.spec_from_file_location("setup_scaffold", SCAFFOLD_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_manifest_is_explicit_unique_and_all_sources_exist():
    module = load_scaffold()
    entries = (*module.CORE_MANIFEST, *module.OPTIONAL_MANIFEST)
    destinations = [entry.destination for entry in entries]

    assert entries
    assert len(destinations) == len(set(destinations))
    assert all((module.TEMPLATE_ROOT / entry.source).is_file() for entry in entries)


def test_core_setup_instantiates_required_docs_and_verifies(tmp_path):
    module = load_scaffold()
    target = tmp_path / "fresh-project"

    result = module.setup(target, profile="core", project_name="Fresh Project")

    assert result.profile == "core"
    for relative_path in module.REQUIRED_CORE_PATHS:
        assert (target / relative_path).is_file(), relative_path
    assert "Fresh Project" in (target / "README.md").read_text(encoding="utf-8")
    assert "{{" not in (target / "README.md").read_text(encoding="utf-8")
    assert not (target / "docs" / "templates" / "README模板.md").exists()
    assert module.verify(target, profile="core", require_hooks=False) == []


def test_optional_profile_is_core_plus_optional(tmp_path):
    module = load_scaffold()
    target = tmp_path / "team-project"

    module.setup(target, profile="optional", project_name="Team Project")

    core_destinations = {entry.destination for entry in module.CORE_MANIFEST}
    optional_destinations = {entry.destination for entry in module.OPTIONAL_MANIFEST}
    assert core_destinations < core_destinations | optional_destinations
    assert all(
        (target / relative_path).is_file() for relative_path in optional_destinations
    )
    assert module.verify(target, profile="optional", require_hooks=False) == []


def test_non_empty_target_is_refused_without_force_and_preserved_with_force(tmp_path):
    module = load_scaffold()
    target = tmp_path / "occupied"
    target.mkdir()
    unrelated = target / "keep.txt"
    unrelated.write_text("owner data", encoding="utf-8")

    with pytest.raises(module.ScaffoldError, match="非空"):
        module.setup(target, profile="core", project_name="Blocked")

    module.setup(target, profile="core", project_name="Allowed", force=True)
    assert unrelated.read_text(encoding="utf-8") == "owner data"


def test_verify_fails_closed_when_payload_is_damaged(tmp_path):
    module = load_scaffold()
    target = tmp_path / "damaged"
    module.setup(target, profile="core", project_name="Damaged")
    (target / ".pre-commit-config.yaml").unlink()

    errors = module.verify(target, profile="core", require_hooks=False)

    assert errors
    assert any(".pre-commit-config.yaml" in error for error in errors)


def test_verify_rejects_incomplete_receipt_manifest(tmp_path):
    module = load_scaffold()
    target = tmp_path / "bad-receipt"
    module.setup(target, profile="core", project_name="Bad Receipt")
    receipt = target / ".devguard-receipt.json"
    receipt.write_text(
        '{"schema": 1, "profile": "core", "files": []}\n',
        encoding="utf-8",
    )

    errors = module.verify(target, profile="core", require_hooks=False)

    assert any("回执缺 manifest 文件" in error for error in errors)


def test_physical_template_payload_has_no_generated_or_backup_files():
    payload = REPO_ROOT / "docs" / "templates" / "devguard"
    forbidden = [
        path
        for path in payload.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".tmp", ".bak"}
    ]
    assert forbidden == []


def test_payload_closes_ci_dependencies_and_documents_both_hooks(tmp_path):
    module = load_scaffold()
    target = tmp_path / "closed"
    module.setup(target, profile="core", project_name="Closed")
    workflow = (target / ".github/workflows/devguard.yml").read_text(encoding="utf-8")
    requirements = (target / "requirements-dev.txt").read_text(encoding="utf-8")
    readme = (target / "README.md").read_text(encoding="utf-8")

    assert "pip install -r requirements-dev.txt" in workflow
    assert "python scripts/devguard.py verify" in workflow
    assert (
        "pytest" in requirements
        and "pre-commit" in requirements
        and "ruff" in requirements
    )
    assert "--hook-type pre-commit" in readme
    assert "--hook-type commit-msg" in readme


def test_cli_e2e_initializes_and_verify_only_checks_same_target(tmp_path):
    target = tmp_path / "cli-project"
    create = subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD_PATH),
            str(target),
            "--profile",
            "core",
            "--project-name",
            "CLI Project",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    verify = subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD_PATH),
            str(target),
            "--profile",
            "core",
            "--verify",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert create.returncode == 0, create.stdout + create.stderr
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert "VERIFY OK" in verify.stdout
