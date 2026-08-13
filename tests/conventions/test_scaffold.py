"""Scaffold contract tests: deployable payload, safe writes, and fail-closed verify."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_PATH = REPO_ROOT / "scripts" / "setup_scaffold.py"
INSTALL_HOOKS_PATH = (
    REPO_ROOT
    / "docs"
    / "templates"
    / "devguard"
    / "scaffold"
    / "core"
    / "scripts"
    / "install_hooks.py"
)


def load_scaffold():
    spec = importlib.util.spec_from_file_location("setup_scaffold", SCAFFOLD_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_install_hooks():
    spec = importlib.util.spec_from_file_location("install_hooks", INSTALL_HOOKS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
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
    assert (target / "AGENTS.md").is_file()
    assert (target / ".agents/skills/devguard/SKILL.md").is_file()
    assert (target / ".agents/skills/devguard/agents/openai.yaml").is_file()
    assert (target / ".codex/config.toml").is_file()
    assert "skills-first" in (target / "AGENTS.md").read_text(encoding="utf-8")
    assert "conventions/README.md" in (target / ".agents/skills/devguard/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert module.verify(target, profile="core", require_hooks=False) == []


def test_optional_profile_is_core_plus_optional(tmp_path):
    module = load_scaffold()
    target = tmp_path / "team-project"

    module.setup(target, profile="optional", project_name="Team Project")

    core_destinations = {entry.destination for entry in module.CORE_MANIFEST}
    optional_destinations = {entry.destination for entry in module.OPTIONAL_MANIFEST}
    assert core_destinations < core_destinations | optional_destinations
    assert all((target / relative_path).is_file() for relative_path in optional_destinations)
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


def test_setup_rolls_back_every_managed_write_when_atomic_replace_fails(tmp_path, monkeypatch):
    module = load_scaffold()
    target = tmp_path / "occupied"
    target.mkdir()
    readme = target / "README.md"
    readme.write_text("owner README\n", encoding="utf-8")
    unrelated = target / "keep.txt"
    unrelated.write_text("owner data\n", encoding="utf-8")
    real_atomic_write = module._atomic_write
    calls = 0

    def fail_after_two_writes(path, payload):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("injected atomic write failure")
        real_atomic_write(path, payload)

    monkeypatch.setattr(module, "_atomic_write", fail_after_two_writes)

    with pytest.raises(module.ScaffoldError, match="已回滚"):
        module.setup(target, profile="core", project_name="Rollback", force=True)

    assert readme.read_text(encoding="utf-8") == "owner README\n"
    assert unrelated.read_text(encoding="utf-8") == "owner data\n"
    assert not (target / ".devguard.json").exists()
    assert not (target / ".devguard-receipt.json").exists()
    assert list(target.rglob("*.devguard.tmp")) == []


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
    hook_installer = (target / "scripts/install_hooks.py").read_text(encoding="utf-8")

    assert "pip install -r requirements-dev.txt" in workflow
    assert "python scripts/devguard.py verify" in workflow
    assert "pytest" in requirements and "pre-commit" in requirements and "ruff" in requirements
    assert "scripts\\install_hooks.py --root ." in readme
    assert '"pre-commit"' in hook_installer
    assert '"commit-msg"' in hook_installer


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


def test_cli_dry_run_validates_and_lists_payload_without_writing(tmp_path):
    target = tmp_path / "planned-project"
    result = subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD_PATH),
            str(target),
            "--profile",
            "core",
            "--project-name",
            "Planned Project",
            "--dry-run",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PLAN OK" in result.stdout
    assert "AGENTS.md" in result.stdout
    assert not target.exists()


def test_isolated_git_config_environment_preserves_parent_and_hides_global_hooks(
    tmp_path, monkeypatch
):
    module = load_install_hooks()
    target = tmp_path / "project"
    (target / ".git").mkdir(parents=True)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "owner-global")
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", "owner-system")

    environment = module._isolated_git_config_environment(target)

    assert os.environ["GIT_CONFIG_GLOBAL"] == "owner-global"
    assert os.environ["GIT_CONFIG_SYSTEM"] == "owner-system"
    assert environment is not os.environ
    for key in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"):
        isolated = Path(environment[key])
        assert isolated.is_file()
        assert isolated.read_text(encoding="utf-8") == ""


def test_external_hooks_are_chained_without_losing_devguard_hooks(tmp_path):
    module = load_install_hooks()
    target = tmp_path / "project"
    local_hooks = target / ".git" / "hooks"
    external_hooks = tmp_path / "ecc-hooks"
    local_hooks.mkdir(parents=True)
    external_hooks.mkdir()
    (local_hooks / "pre-commit").write_text(
        "#!/usr/bin/env bash\necho devguard\n",
        encoding="utf-8",
    )
    (external_hooks / "pre-commit").write_text(
        "#!/usr/bin/env bash\necho ecc-secret-scan\n",
        encoding="utf-8",
    )
    (external_hooks / "pre-push").write_text(
        "#!/usr/bin/env bash\necho ecc-verify\n",
        encoding="utf-8",
    )

    module._chain_external_hooks(target, external_hooks)

    assert (local_hooks / "pre-commit.devguard").is_file()
    pre_commit = (local_hooks / "pre-commit").read_text(encoding="utf-8")
    assert external_hooks.as_posix() in pre_commit
    assert "pre-commit.devguard" in pre_commit
    pre_push = (local_hooks / "pre-push").read_text(encoding="utf-8")
    assert external_hooks.as_posix() in pre_push


def test_verify_rejects_hooks_that_git_will_ignore_without_local_hook_path(tmp_path):
    module = load_scaffold()
    target = tmp_path / "ignored-hooks"
    module.setup(target, profile="core", project_name="Ignored Hooks")
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    hooks = target / ".git" / "hooks"
    for name in ("pre-commit", "commit-msg"):
        (hooks / name).write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    errors = module.verify(target, profile="core", require_hooks=True)

    assert any("core.hooksPath" in error for error in errors)
    subprocess.run(
        ["git", "config", "--local", "core.hooksPath", hooks.as_posix()],
        cwd=target,
        check=True,
    )
    assert module.verify(target, profile="core", require_hooks=True) == []


def test_install_prechecks_ensurepip_before_creating_venv(tmp_path, monkeypatch):
    """2026-08-13 方案③：ensurepip 预检 fail-closed——预检失败时不创建任何产物。"""
    module = load_scaffold()
    target = tmp_path / "t"
    target.mkdir()
    real_run = module.subprocess.run

    def fake_run(command, **kwargs):
        if command[1:3] == ["-m", "ensurepip"]:
            return module.subprocess.CompletedProcess(command, returncode=1)
        return real_run(command, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    with pytest.raises(module.ScaffoldError, match="ensurepip 不可用"):
        module.install(target)

    assert not (target / ".venv").exists()
    assert not (target / ".git").exists()


def test_install_cleans_partial_venv_and_git_on_failure(tmp_path, monkeypatch):
    """2026-08-13 方案③：安装事务失败时清理本次创建的 .venv 与 .git。"""
    module = load_scaffold()
    target = tmp_path / "t"
    target.mkdir()
    real_run = module._run
    calls = 0

    def fail_at_pip(command, *, cwd):
        nonlocal calls
        calls += 1
        if calls == 3:  # git init / venv 之后，pip install 时
            raise module.ScaffoldError("injected pip failure")
        real_run(command, cwd=cwd)

    monkeypatch.setattr(module, "_run", fail_at_pip)

    with pytest.raises(module.ScaffoldError, match="已清理本次产物"):
        module.install(target)

    assert not (target / ".venv").exists()
    assert not (target / ".git").exists()


def test_manifest_covers_all_payload_files():
    """2026-08-13 方案③：manifest 反向校验——载荷目录每个物理文件都被显式声明。"""
    module = load_scaffold()
    declared = {entry.source for entry in (*module.CORE_MANIFEST, *module.OPTIONAL_MANIFEST)}
    payload_roots = (
        module.TEMPLATE_ROOT / "scaffold" / "core",
        module.TEMPLATE_ROOT / "scaffold" / "optional",
    )
    physical = {
        path.relative_to(module.TEMPLATE_ROOT).as_posix()
        for root in payload_roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    undeclared = sorted(physical - declared)
    assert undeclared == [], (
        f"载荷目录存在未在 manifest 声明的文件: {undeclared}（新增模板必须登记 manifest）"
    )
