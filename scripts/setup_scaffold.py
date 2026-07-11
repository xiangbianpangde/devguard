#!/usr/bin/env python3
"""Create a self-contained DevGuard baseline in a fresh project.

The manifest is deliberately explicit. A missing source aborts before the first
write, ``--dry-run`` validates without mutation, and a non-empty target is
rejected unless the caller opts in with ``--force``. Managed writes are atomic
and roll back as one transaction. ``--install`` is the one-command path: it also
creates a local virtual environment, initializes Git, installs dependencies,
installs both hook types, and performs a fail-closed verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import venv
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "docs" / "templates" / "devguard" / "scaffold"
TOKEN_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")
FORBIDDEN_PAYLOAD_NAMES = {"__pycache__"}
FORBIDDEN_PAYLOAD_SUFFIXES = {".bak", ".pyc", ".tmp"}


class ScaffoldError(RuntimeError):
    """Raised when scaffold creation or verification cannot be trusted."""


@dataclass(frozen=True)
class ManifestEntry:
    """One explicit source-to-destination mapping."""

    source: str
    destination: str
    render: bool = False


@dataclass(frozen=True)
class SetupResult:
    """Observable result returned by :func:`setup`."""

    target: Path
    profile: str
    written: tuple[str, ...]


CORE_MANIFEST: tuple[ManifestEntry, ...] = (
    ManifestEntry("core/.gitattributes", ".gitattributes"),
    ManifestEntry("core/.gitignore", ".gitignore"),
    ManifestEntry("core/.pre-commit-config.yaml", ".pre-commit-config.yaml"),
    ManifestEntry("core/devguard.json.tmpl", ".devguard.json", render=True),
    ManifestEntry(
        "core/.github/workflows/devguard.yml", ".github/workflows/devguard.yml"
    ),
    ManifestEntry("core/README.md.tmpl", "README.md", render=True),
    ManifestEntry("core/STATUS.md.tmpl", "STATUS.md", render=True),
    ManifestEntry("core/CLAUDE.md.tmpl", "CLAUDE.md", render=True),
    ManifestEntry("core/AGENTS.md.tmpl", "AGENTS.md", render=True),
    ManifestEntry(
        "core/.agents/skills/devguard/SKILL.md.tmpl",
        ".agents/skills/devguard/SKILL.md",
        render=True,
    ),
    ManifestEntry(
        "core/.agents/skills/devguard/agents/openai.yaml",
        ".agents/skills/devguard/agents/openai.yaml",
    ),
    ManifestEntry("core/.codex/config.toml", ".codex/config.toml"),
    ManifestEntry("core/CONTRIBUTING.md", "CONTRIBUTING.md"),
    ManifestEntry("core/SECURITY.md", "SECURITY.md"),
    ManifestEntry("core/requirements-dev.txt", "requirements-dev.txt"),
    ManifestEntry("core/conventions/README.md", "conventions/README.md"),
    ManifestEntry("core/docs/plan/背景.md.tmpl", "docs/plan/背景.md", render=True),
    ManifestEntry(
        "core/docs/plan/开发清单.md.tmpl", "docs/plan/开发清单.md", render=True
    ),
    ManifestEntry("core/scripts/devguard.py", "scripts/devguard.py"),
    ManifestEntry("core/scripts/install_hooks.py", "scripts/install_hooks.py"),
    ManifestEntry(
        "core/tests/governance/test_devguard.py", "tests/governance/test_devguard.py"
    ),
    ManifestEntry("core/worklogs/.gitkeep", "worklogs/.gitkeep"),
)

OPTIONAL_MANIFEST: tuple[ManifestEntry, ...] = (
    ManifestEntry("optional/.github/CODEOWNERS", ".github/CODEOWNERS"),
    ManifestEntry("optional/docs/reports/.gitkeep", "docs/reports/.gitkeep"),
    ManifestEntry("optional/docs/decisions/.gitkeep", "docs/decisions/.gitkeep"),
)

REQUIRED_CORE_PATHS: tuple[str, ...] = tuple(
    entry.destination for entry in CORE_MANIFEST
)
REQUIRED_OPTIONAL_PATHS: tuple[str, ...] = tuple(
    entry.destination for entry in OPTIONAL_MANIFEST
)


def entries_for(profile: str) -> tuple[ManifestEntry, ...]:
    """Return the complete manifest for a named profile."""
    if profile == "core":
        return CORE_MANIFEST
    if profile == "optional":
        return CORE_MANIFEST + OPTIONAL_MANIFEST
    raise ScaffoldError(f"未知 profile：{profile!r}（只能是 core 或 optional）")


def _validate_sources(entries: Sequence[ManifestEntry]) -> None:
    missing = [
        entry.source
        for entry in entries
        if not (TEMPLATE_ROOT / entry.source).is_file()
    ]
    if missing:
        raise ScaffoldError(f"manifest 源文件缺失，未写入任何文件：{missing}")

    destinations = [entry.destination for entry in entries]
    duplicates = sorted({path for path in destinations if destinations.count(path) > 1})
    if duplicates:
        raise ScaffoldError(f"manifest 目标重复，未写入任何文件：{duplicates}")

    forbidden = [
        path
        for path in TEMPLATE_ROOT.rglob("*")
        if path.name in FORBIDDEN_PAYLOAD_NAMES
        or path.suffix in FORBIDDEN_PAYLOAD_SUFFIXES
    ]
    if forbidden:
        raise ScaffoldError(f"模板载荷含临时/生成文件，未写入任何文件：{forbidden}")


def _render_text(text: str, project_name: str, profile: str) -> str:
    rendered = (
        text.replace("{{PROJECT_NAME}}", project_name)
        .replace("{{PROFILE}}", profile)
        .replace("{{DATE}}", date.today().isoformat())
    )
    unresolved = sorted(set(TOKEN_PATTERN.findall(rendered)))
    if unresolved:
        raise ScaffoldError(f"模板仍有未解析变量：{unresolved}")
    return rendered


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _receipt_payload(result: SetupResult, payloads: dict[str, bytes]) -> bytes:
    receipt = {
        "schema": 1,
        "profile": result.profile,
        "files": [
            {"path": relative_path, "sha256": _sha256_bytes(payloads[relative_path])}
            for relative_path in result.written
        ],
    }
    return (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    """Replace one file atomically without exposing a partially written payload."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".devguard.tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _rollback_writes(
    target: Path,
    previous: dict[str, bytes | None],
    written: Sequence[str],
) -> None:
    """Restore prior bytes and remove files created by a failed transaction."""
    for relative in reversed(written):
        path = target / relative
        original = previous[relative]
        if original is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_write(path, original)

    directories = sorted(
        {parent for relative in written for parent in (target / relative).parents},
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        if directory == target.parent or target not in (directory, *directory.parents):
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def _build_payloads(
    entries: Sequence[ManifestEntry], project_name: str, profile: str
) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    for entry in entries:
        source = TEMPLATE_ROOT / entry.source
        if entry.render:
            content = _render_text(
                source.read_text(encoding="utf-8"), project_name, profile
            )
            payloads[entry.destination] = content.encode("utf-8")
        else:
            payloads[entry.destination] = source.read_bytes()
    return payloads


def _validate_receipt(
    target: Path,
    *,
    profile: str,
    check_hashes: bool,
) -> list[str]:
    """Validate receipt closure; hashes are immutable only during creation.

    A later ``--verify`` must allow owners to edit generated files, so it checks
    the manifest and digest syntax but not equality. ``setup`` performs the
    stronger byte-for-byte check before returning success.
    """
    path = target / ".devguard-receipt.json"
    if not path.is_file():
        return ["缺少初始化回执：.devguard-receipt.json"]
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"初始化回执不可解析：{error}"]
    if not isinstance(receipt, dict):
        return ["初始化回执必须是 JSON object"]

    errors: list[str] = []
    if receipt.get("schema") != 1:
        errors.append("初始化回执 schema 必须为 1")
    if receipt.get("profile") != profile:
        errors.append(
            f"初始化回执 profile={receipt.get('profile')!r} 与目标 {profile!r} 不一致"
        )
    records = receipt.get("files")
    if not isinstance(records, list):
        return [*errors, "初始化回执 files 必须是数组"]

    expected = {entry.destination for entry in entries_for(profile)}
    seen: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append("初始化回执含非 object 文件记录")
            continue
        relative = record.get("path")
        digest = record.get("sha256")
        if not isinstance(relative, str) or not relative:
            errors.append("初始化回执含空文件路径")
            continue
        if relative in seen:
            errors.append(f"初始化回执重复文件：{relative}")
            continue
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"初始化回执摘要无效：{relative}")
            continue
        seen[relative] = digest

    missing = sorted(expected - set(seen))
    extra = sorted(set(seen) - expected)
    if missing:
        errors.append(f"初始化回执缺 manifest 文件：{missing}")
    if extra:
        errors.append(f"初始化回执含 manifest 外文件：{extra}")
    if check_hashes:
        for relative in sorted(expected & set(seen)):
            generated = target / relative
            if not generated.is_file() or _sha256(generated) != seen[relative]:
                errors.append(f"初始化写入后摘要不一致：{relative}")
    return errors


def setup(
    target: Path,
    *,
    profile: str,
    project_name: str,
    force: bool = False,
) -> SetupResult:
    """Write a profile into ``target`` and verify it before returning."""
    target = target.resolve()
    entries = entries_for(profile)
    _validate_sources(entries)
    if not project_name.strip():
        raise ScaffoldError("project name 不能为空")
    if target.exists() and not target.is_dir():
        raise ScaffoldError(f"目标路径不是目录：{target}")
    if target.exists() and any(target.iterdir()) and not force:
        raise ScaffoldError(f"目标目录非空：{target}；确认覆盖时显式传 --force")

    payloads = _build_payloads(entries, project_name, profile)
    result = SetupResult(
        target=target,
        profile=profile,
        written=tuple(entry.destination for entry in entries),
    )
    payloads[".devguard-receipt.json"] = _receipt_payload(result, payloads)

    previous: dict[str, bytes | None] = {}
    for relative in payloads:
        destination = target / relative
        if destination.exists() and not destination.is_file():
            raise ScaffoldError(f"manifest 目标不是普通文件：{destination}")
        previous[relative] = destination.read_bytes() if destination.is_file() else None

    written: list[str] = []
    try:
        for relative, payload in payloads.items():
            _atomic_write(target / relative, payload)
            written.append(relative)

        receipt_errors = _validate_receipt(target, profile=profile, check_hashes=True)
        if receipt_errors:
            raise ScaffoldError(
                "初始化回执校验失败：\n- " + "\n- ".join(receipt_errors)
            )
        errors = verify(target, profile=profile, require_hooks=False)
        if errors:
            raise ScaffoldError("初始化后校验失败：\n- " + "\n- ".join(errors))
    except Exception as error:
        try:
            _rollback_writes(target, previous, written)
        except Exception as rollback_error:
            raise ScaffoldError(
                f"初始化事务失败，回滚也失败：{error}; rollback={rollback_error}"
            ) from error
        raise ScaffoldError(f"初始化事务失败，已回滚：{error}") from error
    return result


def _read_profile(target: Path) -> str | None:
    config_path = target / ".devguard.json"
    if not config_path.is_file():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    profile = data.get("profile")
    return profile if isinstance(profile, str) else None


def verify(target: Path, *, profile: str | None, require_hooks: bool) -> list[str]:
    """Return all verification errors; an empty list is the only success state."""
    target = target.resolve()
    effective_profile = profile or _read_profile(target)
    errors: list[str] = []
    if effective_profile not in {"core", "optional"}:
        return ["无法从 .devguard.json 确定 profile"]

    for entry in entries_for(effective_profile):
        path = target / entry.destination
        if not path.is_file():
            errors.append(f"缺少 manifest 文件：{entry.destination}")
            continue
        if entry.render and TOKEN_PATTERN.search(path.read_text(encoding="utf-8")):
            errors.append(f"仍含模板变量：{entry.destination}")

    errors.extend(
        _validate_receipt(target, profile=effective_profile, check_hashes=False)
    )

    generated_verifier = target / "scripts" / "devguard.py"
    if generated_verifier.is_file():
        command = [
            sys.executable,
            str(generated_verifier),
            "verify",
            "--root",
            str(target),
        ]
        if require_hooks:
            command.append("--require-hooks")
        result = subprocess.run(
            command,
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip()
            errors.append(f"目标自检失败：{detail or '无诊断输出'}")
    elif not any("scripts/devguard.py" in error for error in errors):
        errors.append("缺少目标自检器：scripts/devguard.py")
    return errors


def _venv_python(target: Path) -> Path:
    windows = target / ".venv" / "Scripts" / "python.exe"
    posix = target / ".venv" / "bin" / "python"
    return windows if windows.is_file() else posix


def _run(command: Sequence[str], *, cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        raise ScaffoldError(
            f"命令失败（exit={result.returncode}）：{' '.join(command)}"
        )


def install(target: Path) -> None:
    """Create an isolated toolchain and install both Git hook stages."""
    target = target.resolve()
    _run(["git", "init"], cwd=target)
    venv.EnvBuilder(with_pip=True).create(target / ".venv")
    python = _venv_python(target)
    if not python.is_file():
        raise ScaffoldError("虚拟环境创建后找不到 Python")
    _run(
        [str(python), "-m", "pip", "install", "-r", "requirements-dev.txt"], cwd=target
    )
    _run(
        [
            str(python),
            "scripts/install_hooks.py",
            "--root",
            str(target),
        ],
        cwd=target,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="一键初始化可验证的 DevGuard 项目基线")
    parser.add_argument("target", type=Path, help="目标项目根目录")
    parser.add_argument("--profile", choices=("core", "optional"))
    parser.add_argument("--project-name", help="项目名；默认使用目标目录名")
    parser.add_argument(
        "--force", action="store_true", help="允许写入非空目录并覆盖同名文件"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="创建 .venv、git init、安装依赖和双阶段 hooks",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只验证并列出将写入的 manifest，不创建或修改目标",
    )
    parser.add_argument(
        "--verify", action="store_true", help="不写文件，只校验既有目标"
    )
    parser.add_argument(
        "--require-hooks",
        action="store_true",
        help="校验时同时要求 pre-commit 和 commit-msg 已安装",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = args.target.resolve()
    profile = args.profile or (None if args.verify else "core")
    try:
        if args.dry_run:
            if args.verify or args.install:
                raise ScaffoldError("--dry-run 不能与 --verify/--install 同时使用")
            if profile is None:
                raise ScaffoldError("dry-run 模式缺 profile")
            entries = entries_for(profile)
            _validate_sources(entries)
            _build_payloads(entries, args.project_name or target.name, profile)
            print(f"PLAN OK: {target} ({profile}, {len(entries)} files)")
            for entry in entries:
                print(f"- {entry.destination}")
            return 0
        if args.verify:
            errors = verify(
                target,
                profile=profile,
                require_hooks=args.require_hooks,
            )
            if errors:
                print("VERIFY FAILED\n- " + "\n- ".join(errors), file=sys.stderr)
                return 1
            verified_profile = profile or _read_profile(target)
            print(f"VERIFY OK: {target} ({verified_profile})")
            return 0

        if profile is None:  # Defensive: non-verify mode always supplies a profile.
            raise ScaffoldError("初始化模式缺 profile")
        result = setup(
            target,
            profile=profile,
            project_name=args.project_name or target.name,
            force=args.force,
        )
        if args.install:
            install(target)
            errors = verify(target, profile=profile, require_hooks=True)
            if errors:
                raise ScaffoldError("安装后校验失败：\n- " + "\n- ".join(errors))
        print(f"INIT OK: {target} ({result.profile}, {len(result.written)} files)")
        if not args.install:
            print("完整一键安装：在同一命令追加 --install（会创建 .venv 并访问依赖源）")
        return 0
    except ScaffoldError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
