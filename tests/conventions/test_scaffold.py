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
        hook = hooks / name
        hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)  # R5-02：钩子需可执行位（0644 被 git 静默忽略）

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
    # 2026-08-13 R-09：TEMPLATE_ROOT 已含 scaffold，正确路径为 TEMPLATE_ROOT/core 与 /optional
    payload_roots = (
        module.TEMPLATE_ROOT / "core",
        module.TEMPLATE_ROOT / "optional",
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


def test_install_failure_rolls_back_setup_payloads_too(tmp_path, monkeypatch):
    """2026-08-13 R-03：install 中段失败 → setup 写入的 payload 一并回滚，target 归零。"""
    module = load_scaffold()
    target = tmp_path / "t"
    target.mkdir()
    owner_file = target / "README.md"
    owner_file.write_text("owner README\n", encoding="utf-8")
    real_run = module._run
    calls = 0

    def fail_at_pip(command, *, cwd):
        nonlocal calls
        calls += 1
        if calls == 3:  # git init / venv 之后，pip install 时
            raise module.ScaffoldError("injected pip failure")
        real_run(command, cwd=cwd)

    monkeypatch.setattr(module, "_run", fail_at_pip)

    # 红队第二轮要求：--force 真跑（目标含 owner 文件，setup 需覆盖写入）
    returncode = module.main([str(target), "--profile", "core", "--install", "--force"])
    assert returncode == 1

    # payload 全部回滚（含 receipt）+ owner 文件恢复 + venv/git 清理 → target 归零
    assert not (target / ".devguard.json").exists()
    assert not (target / ".devguard-receipt.json").exists()
    assert not (target / "STATUS.md").exists()
    assert not (target / "CLAUDE.md").exists()
    assert not (target / ".venv").exists()
    assert not (target / ".git").exists()
    assert owner_file.read_text(encoding="utf-8") == "owner README\n"
    assert sorted(p.name for p in target.iterdir()) == ["README.md"]


def test_final_verify_failure_after_install_rolls_back_too(tmp_path, monkeypatch):
    """2026-08-13 红队第三轮 R-03 终修：install 成功后 final verify 失败 → 全量回滚归零。"""
    module = load_scaffold()
    target = tmp_path / "t"
    target.mkdir()
    owner_file = target / "README.md"
    owner_file.write_text("owner README\n", encoding="utf-8")

    def fake_verify(target_path, *, profile, require_hooks):
        # install() 内部的 verify 通过（profile=None）；main 的 final verify 失败
        if profile is None:
            return []
        return ["injected final verify failure"]

    monkeypatch.setattr(module, "verify", fake_verify)

    returncode = module.main([str(target), "--profile", "core", "--install", "--force"])
    assert returncode == 1

    # payload（含 receipt）全部回滚 + owner 文件恢复 + venv/git 清理 → target 归零
    assert not (target / ".devguard.json").exists()
    assert not (target / ".devguard-receipt.json").exists()
    assert not (target / "STATUS.md").exists()
    assert not (target / ".venv").exists()
    assert not (target / ".git").exists()
    assert owner_file.read_text(encoding="utf-8") == "owner README\n"
    assert sorted(p.name for p in target.iterdir()) == ["README.md"]


def test_gitleaks_config_uses_extend_mode_not_rule_copy():
    """2026-08-13 红队 N-1：extend 模式防规则集腐化——禁止回退到复制默认规则。"""
    root_config = REPO_ROOT / ".gitleaks.toml"
    content = root_config.read_text(encoding="utf-8")
    # extend 模式必须存在（上游演进自动生效）
    assert "[extend]" in content
    assert "useDefault = true" in content
    # 复制模式必须不存在（[[rules]] 全量复制会随上游腐化）
    assert "[[rules]]" not in content
    # 教学豁免增量保留
    assert "security_demo" in content
    # 镜像逐字节一致
    for mirror in (
        REPO_ROOT / "docs/templates/devguard/.gitleaks.toml",
        REPO_ROOT / "docs/templates/devguard/scaffold/core/.gitleaks.toml",
    ):
        assert mirror.read_bytes() == root_config.read_bytes(), f"镜像漂移: {mirror}"


def test_staging_cleaned_on_failure_when_target_empty(tmp_path, monkeypatch):
    """S-1（红队①/②/S1-A4）：空 target 写入中途失败 → staging 清理、target 零残留。

    staging 敏感（红队 S1-A4 哨兵）：断言每次写入都发生在 staging 路径——
    若实现退化为「直接写 target」，本断言即 FAIL（防止测试 vacuous）。
    """
    module = load_scaffold()
    target = tmp_path / "fresh"
    assert not target.exists()
    real_atomic_write = module._atomic_write
    calls = 0

    def fail_after_three_writes(path, payload):
        nonlocal calls
        # 哨兵：写入必须发生在 staging 目录内（退化为直写 target 时 FAIL）
        assert ".devguard-staging-" in str(path), (
            f"写入路径 {path} 不在 staging（S-1 实现退化或测试失效）"
        )
        calls += 1
        if calls == 3:
            raise OSError("injected staging write failure")
        real_atomic_write(path, payload)

    monkeypatch.setattr(module, "_atomic_write", fail_after_three_writes)

    with pytest.raises(module.ScaffoldError, match="已回滚"):
        module.setup(target, profile="core", project_name="Fresh")

    # 结构性归零：target 不存在 + 无 staging 残骸 + 无临时文件
    assert not target.exists()
    assert list(tmp_path.glob(".devguard-staging-*")) == []
    assert list(tmp_path.glob("*.devguard.tmp")) == []


def test_staging_atomic_commit_leaves_no_residue(tmp_path, monkeypatch):
    """S-1（红队②/④/S1-A4）：成功路径 staging 提交后无残骸，target 完整。

    staging 敏感哨兵：断言 os.replace(staging, target) 被调用一次——
    若实现退化（直写 target），os.replace 不会被调用即 FAIL。
    """
    module = load_scaffold()
    target = tmp_path / "fresh"
    real_replace = os.replace
    replace_calls: list[tuple[object, object]] = []

    def recording_replace(src, dst):
        # 只记录 staging→target 的目录原子提交（文件级原子写不计数）
        if ".devguard-staging-" in str(src) and str(dst) == str(target):
            replace_calls.append((src, dst))
        real_replace(src, dst)

    monkeypatch.setattr(module.os, "replace", recording_replace)

    module.setup(target, profile="core", project_name="Fresh")
    assert target.is_dir()
    assert (target / ".devguard.json").exists()
    assert (target / ".devguard-receipt.json").exists()
    # 哨兵：原子提交必须经 os.replace 完成（且 src 是 staging）
    assert len(replace_calls) == 1, f"os.replace 调用次数 {len(replace_calls)} != 1"
    src, dst = replace_calls[0]
    assert ".devguard-staging-" in str(src)
    assert str(dst) == str(target)
    # 无 staging/临时残骸
    assert list(tmp_path.glob(".devguard-staging-*")) == []
    assert list(tmp_path.glob("*.devguard.tmp")) == []
    # 校验通过
    assert module.verify(target, profile="core", require_hooks=False) == []


def test_staging_failure_with_eacces_cleans_up(tmp_path, monkeypatch):
    """S-1 矩阵⑥：staging 写入 EACCES（权限错误）→ 清理归零（实现行为验证）。"""
    module = load_scaffold()
    target = tmp_path / "fresh"
    real_atomic_write = module._atomic_write
    calls = 0

    def eacces_after_two_writes(path, payload):
        nonlocal calls
        assert ".devguard-staging-" in str(path), "写入必须在 staging"
        calls += 1
        if calls == 2:
            raise PermissionError(13, "Permission denied")  # EACCES
        real_atomic_write(path, payload)

    monkeypatch.setattr(module, "_atomic_write", eacces_after_two_writes)

    with pytest.raises(module.ScaffoldError):
        module.setup(target, profile="core", project_name="Fresh")

    assert not target.exists()
    assert list(tmp_path.glob(".devguard-staging-*")) == []


def test_project_name_rejects_injection_and_accepts_valid(tmp_path):
    """R2-13（红队第五轮）：project_name 白名单——JSON 破坏/换行/markdown 注入拦截，合法名通过。"""
    module = load_scaffold()
    for bad in ('X"}]},{broken', "a\nb", "<script>alert(1)</script>", "A" * 100):
        with pytest.raises(module.ScaffoldError, match="非法字符"):
            module.setup(tmp_path / "t", profile="core", project_name=bad)
    result = module.setup(tmp_path / "ok", profile="core", project_name="My Project-2026")
    assert (tmp_path / "ok").is_dir()
    assert result.profile == "core"


def test_uninstall_restores_owner_hooks_through_reinstall(tmp_path, monkeypatch):
    """R5-17（红队第五批数据丢失级回归）：install→uninstall→reinstall 后 owner 钩子完整。

    场景：owner 钩子被 install 暂存为 .devguard → uninstall 还原 →
    reinstall 后 owner 钩子仍在（不丢失）。
    """
    module = load_scaffold()
    target = tmp_path / "t"
    module.setup(target, profile="core", project_name="Hook Cycle")
    subprocess.run(["git", "init", "-q"], cwd=target, check=True)
    hooks = target / ".git" / "hooks"
    owner_hook = hooks / "pre-push"
    owner_hook.write_text("#!/bin/sh\necho OWNER-HOOK\n", encoding="utf-8")
    owner_hook.chmod(0o755)
    original = owner_hook.read_text(encoding="utf-8")

    # install（ECC 不存在时 owner pre-push 会被 DevGuard 组合包装器覆盖/暂存？模拟暂存）
    devguard_backup = hooks / "pre-push.devguard"
    if not devguard_backup.exists():
        owner_hook.replace(devguard_backup)
    wrapper = hooks / "pre-push"
    wrapper.write_text("#!/usr/bin/env bash\n# DevGuard composed hook\nfake\n", encoding="utf-8")
    wrapper.chmod(0o755)

    # uninstall：还原暂存
    verifier = target / "scripts" / "devguard.py"
    r = subprocess.run(
        [sys.executable, str(verifier), "uninstall", "--root", str(target)],
        cwd=target,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert owner_hook.read_text(encoding="utf-8") == original, "owner 钩子未被还原"
    assert not devguard_backup.exists()

    # reinstall（再次模拟暂存+卸载循环）：owner 内容仍完整
    owner_hook.replace(devguard_backup)
    wrapper.write_text("#!/usr/bin/env bash\n# DevGuard composed hook\nfake2\n", encoding="utf-8")
    r2 = subprocess.run(
        [sys.executable, str(verifier), "uninstall", "--root", str(target)],
        cwd=target,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0
    assert owner_hook.read_text(encoding="utf-8") == original, "循环后 owner 钩子丢失"
