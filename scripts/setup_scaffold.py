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
import secrets
import shutil
import dataclasses
import subprocess
import sys
import tempfile
import venv
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# Windows 中文 stdout 兼容（cp1252 下打印中文会 UnicodeEncodeError）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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
    # 2026-08-13 R-03：被覆盖文件的原始字节备份（install 失败时跨阶段回滚用）
    previous: dict[str, bytes | None] = dataclasses.field(default_factory=dict)


CORE_MANIFEST: tuple[ManifestEntry, ...] = (
    ManifestEntry("core/.gitattributes", ".gitattributes"),
    ManifestEntry("core/.gitignore", ".gitignore"),
    # 2026-08-13 R-01/R-02：gitleaks 全量规则集（与真源逐字节镜像）
    ManifestEntry("core/.gitleaks.toml", ".gitleaks.toml"),
    ManifestEntry("core/.pre-commit-config.yaml", ".pre-commit-config.yaml"),
    ManifestEntry("core/devguard.json.tmpl", ".devguard.json", render=True),
    ManifestEntry("core/.github/workflows/devguard.yml", ".github/workflows/devguard.yml"),
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
    ManifestEntry("core/docs/plan/开发清单.md.tmpl", "docs/plan/开发清单.md", render=True),
    ManifestEntry("core/scripts/devguard.py", "scripts/devguard.py"),
    ManifestEntry("core/scripts/install_hooks.py", "scripts/install_hooks.py"),
    ManifestEntry("core/tests/governance/test_devguard.py", "tests/governance/test_devguard.py"),
    ManifestEntry("core/worklogs/.gitkeep", "worklogs/.gitkeep"),
)

OPTIONAL_MANIFEST: tuple[ManifestEntry, ...] = (
    ManifestEntry("optional/.github/CODEOWNERS", ".github/CODEOWNERS"),
    ManifestEntry("optional/docs/reports/.gitkeep", "docs/reports/.gitkeep"),
    ManifestEntry("optional/docs/decisions/.gitkeep", "docs/decisions/.gitkeep"),
)

REQUIRED_CORE_PATHS: tuple[str, ...] = tuple(entry.destination for entry in CORE_MANIFEST)
REQUIRED_OPTIONAL_PATHS: tuple[str, ...] = tuple(entry.destination for entry in OPTIONAL_MANIFEST)


def entries_for(profile: str) -> tuple[ManifestEntry, ...]:
    """Return the complete manifest for a named profile."""
    if profile == "core":
        return CORE_MANIFEST
    if profile == "optional":
        return CORE_MANIFEST + OPTIONAL_MANIFEST
    raise ScaffoldError(f"未知 profile：{profile!r}（只能是 core 或 optional）")


def _validate_sources(entries: Sequence[ManifestEntry]) -> None:
    missing = [entry.source for entry in entries if not (TEMPLATE_ROOT / entry.source).is_file()]
    if missing:
        raise ScaffoldError(f"manifest 源文件缺失，未写入任何文件：{missing}")

    destinations = [entry.destination for entry in entries]
    duplicates = sorted({path for path in destinations if destinations.count(path) > 1})
    if duplicates:
        raise ScaffoldError(f"manifest 目标重复，未写入任何文件：{duplicates}")

    forbidden = [
        path
        for path in TEMPLATE_ROOT.rglob("*")
        if path.name in FORBIDDEN_PAYLOAD_NAMES or path.suffix in FORBIDDEN_PAYLOAD_SUFFIXES
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
            content = _render_text(source.read_text(encoding="utf-8"), project_name, profile)
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
        errors.append(f"初始化回执 profile={receipt.get('profile')!r} 与目标 {profile!r} 不一致")
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
    # R2-13（2026-08-14 红队第五轮）：显式白名单校验——
    # 防 JSON 结构破坏（X"}]},{broken DoS）与 markdown/换行注入 AI 入口
    # （CLAUDE.md/AGENTS.md 直接拼 project_name）。仅允许字母数字空格下划线连字符。
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _\-]{0,62}", project_name):
        raise ScaffoldError(
            "project name 含非法字符：仅允许字母/数字/空格/下划线/连字符（≤63 字符）"
        )
    if target.exists() and not target.is_dir():
        raise ScaffoldError(f"目标路径不是目录：{target}")
    if target.exists() and any(target.iterdir()) and not force:
        raise ScaffoldError(f"目标目录非空：{target}；确认覆盖时显式传 --force")

    payloads = _build_payloads(entries, project_name, profile)
    result = SetupResult(
        target=target,
        profile=profile,
        written=tuple(entry.destination for entry in entries),
        previous={},
    )
    payloads[".devguard-receipt.json"] = _receipt_payload(result, payloads)

    # S-1（2026-08-14 红队建议，方案稿 docs/plan/design/设计提案-S1-临时目录构建与原子rename.md）：
    # 空 target 走「staging 完整构建 → 校验通过 → os.replace 原子提交」——
    # 失败 = 删 staging 归零，结构性消灭回滚清单漏项类缺陷（红队 a/c 点）。
    # 非空 target（--force）保持现有回滚清单路径（owner 既有文件覆盖场景）。
    empty_target = not target.exists() or not any(target.iterdir())
    work_root = target
    staging: Path | None = None
    if empty_target:
        staging = target.parent / f".devguard-staging-{secrets.token_hex(4)}"
        staging.mkdir()
        work_root = staging

    previous: dict[str, bytes | None] = {}
    for relative in payloads:
        destination = work_root / relative
        if destination.exists() and not destination.is_file():
            raise ScaffoldError(f"manifest 目标不是普通文件：{destination}")
        previous[relative] = destination.read_bytes() if destination.is_file() else None

    # R-03（2026-08-13 第二轮）：written 必须包含 receipt（运行时注入 payloads），
    # 否则跨阶段回滚会残留 .devguard-receipt.json
    result = SetupResult(
        target=target,
        profile=profile,
        written=tuple(payloads.keys()),
        previous=previous,
    )

    written: list[str] = []
    try:
        for relative, payload in payloads.items():
            _atomic_write(work_root / relative, payload)
            written.append(relative)

        receipt_errors = _validate_receipt(work_root, profile=profile, check_hashes=True)
        if receipt_errors:
            raise ScaffoldError("初始化回执校验失败：\n- " + "\n- ".join(receipt_errors))
        errors = verify(work_root, profile=profile, require_hooks=False)
        if errors:
            raise ScaffoldError("初始化后校验失败：\n- " + "\n- ".join(errors))
        if staging is not None:
            # S-1 原子提交：同文件系统（同级目录）os.replace，空 target 目标不存在
            os.replace(staging, target)
            staging = None
    except Exception as error:
        if staging is not None:
            # S-1：staging 场景删除 staging 即归零（结构性回滚，无需清单）
            shutil.rmtree(staging, ignore_errors=True)
        else:
            # 非空 target（--force）场景：回滚清单恢复 owner 文件
            try:
                _rollback_writes(work_root, previous, written)
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


def verify(
    target: Path,
    *,
    profile: str | None,
    require_hooks: bool,
    check_hashes: bool = False,
) -> list[str]:
    """Return all verification errors; an empty list is the only success state.

    R5-01：check_hashes=True 时强校验（按回执 digest 逐文件比对，篡改可发现）。
    """
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

    errors.extend(_validate_receipt(target, profile=effective_profile, check_hashes=check_hashes))

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
        if check_hashes:
            command.append("--check-hashes")
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
        raise ScaffoldError(f"命令失败（exit={result.returncode}）：{' '.join(command)}")


def install(target: Path) -> None:
    """Create an isolated toolchain and install both Git hook stages.

    失败清理（2026-08-13 蓝队方案③）：任何一步失败时删除本次创建的产物——
    .venv（必然本次创建）与 .git（仅当 git init 前不存在时本次创建），
    不留半成品（技术债 #7）。
    """
    target = target.resolve()
    venv_dir = target / ".venv"
    git_dir = target / ".git"
    git_existed = git_dir.exists()

    # ensurepip 预检（fail-closed，提前失败而非 venv 创建后报错滞后）
    check = subprocess.run(
        [sys.executable, "-m", "ensurepip", "--version"],
        capture_output=True,
        check=False,
    )
    if check.returncode != 0:
        raise ScaffoldError(
            "ensurepip 不可用（无法创建带 pip 的虚拟环境）。"
            "请先修复 Python 环境：Debian/Ubuntu `sudo apt-get install python3-venv`；"
            "其他发行版参考官方文档。"
        )

    try:
        _run(["git", "init"], cwd=target)
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        python = _venv_python(target)
        if not python.is_file():
            raise ScaffoldError("虚拟环境创建后找不到 Python")
        _run(
            [str(python), "-m", "pip", "install", "-r", "requirements-dev.txt"],
            cwd=target,
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
        # R-03（第二轮）：hooks 安装后的最终校验（require_hooks=True），
        # 失败即异常 → main 层跨阶段回滚（不留半成品）
        hook_errors = verify(target, profile=None, require_hooks=True)
        if hook_errors:
            raise ScaffoldError("hooks 安装后校验失败：\n- " + "\n- ".join(hook_errors))
    except Exception as error:
        import shutil

        if venv_dir.exists():
            shutil.rmtree(venv_dir, ignore_errors=True)
        if not git_existed and git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)
        raise ScaffoldError(f"安装事务失败，已清理本次产物：{error}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="一键初始化可验证的 DevGuard 项目基线")
    parser.add_argument("target", type=Path, help="目标项目根目录")
    parser.add_argument("--profile", choices=("core", "optional"))
    parser.add_argument("--project-name", help="项目名；默认使用目标目录名")
    parser.add_argument("--force", action="store_true", help="允许写入非空目录并覆盖同名文件")
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
    parser.add_argument("--verify", action="store_true", help="不写文件，只校验既有目标")
    parser.add_argument(
        "--require-hooks",
        action="store_true",
        help="校验时同时要求 pre-commit 和 commit-msg 已安装",
    )
    parser.add_argument(
        "--check-hashes",
        action="store_true",
        help="R5-01：强校验模式——按回执 digest 逐文件比对（篡改可发现）",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="R5-17：卸载目标项目的 hooks 与隔离环境（委托目标 devguard.py uninstall）",
    )
    return parser


MIN_PYTHON = (3, 10)


def python_guidance() -> str:
    """R-15d：直调入口的版本预检指引（与 install.sh/install.ps1 同款文案）。"""
    return (
        "Python >= 3.10 未满足。请先安装再重试（安装器不会自动安装 Python）：\n"
        "  - macOS:        brew install python@3.12   或 https://www.python.org/downloads/\n"
        "  - Ubuntu/Debian: sudo apt-get install python3 python3-venv\n"
        "  - Fedora:       sudo dnf install python3\n"
        "  - Arch:         sudo pacman -S python\n"
        "  - Windows:      winget install Python.Python.3.12（或使用 scripts/install.ps1）"
    )


def main(argv: Sequence[str] | None = None) -> int:
    if sys.version_info[:2] < MIN_PYTHON:
        print(f"ERROR: {python_guidance()}", file=sys.stderr)
        return 1
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
        if args.uninstall:
            verifier = target / "scripts" / "devguard.py"
            if not verifier.is_file():
                # R5-17（红队第四批）：错误路径必须 rc=1（此前 rc=0 属 fail-open 声称失实）
                print("ERROR: 目标项目缺 scripts/devguard.py（无法卸载）", file=sys.stderr)
                return 1
            result = subprocess.run(
                [sys.executable, str(verifier), "uninstall", "--root", str(target)],
                cwd=target,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            print((result.stdout or result.stderr).strip())
            return result.returncode
        if args.verify:
            errors = verify(
                target,
                profile=profile,
                require_hooks=args.require_hooks,
                check_hashes=args.check_hashes,
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
            try:
                install(target)
                # R-03（第三轮终修）：final verify 纳入同一跨阶段回滚 try——
                # install 成功但末段校验失败（状态化注入场景）也必须回滚归零
                errors = verify(target, profile=profile, require_hooks=True)
                if errors:
                    raise ScaffoldError("安装后校验失败：\n- " + "\n- ".join(errors))
            except ScaffoldError:
                # R-03：install/末段校验失败必须回滚 setup 写下的全部 payload
                # （恢复被覆盖的 owner 文件），不留半成品
                try:
                    _rollback_writes(target, result.previous, list(result.written))
                except Exception as rollback_error:
                    raise ScaffoldError(f"安装失败且跨阶段回滚失败：{rollback_error}") from None
                raise
        print(f"INIT OK: {target} ({result.profile}, {len(result.written)} files)")
        if not args.install:
            print("完整一键安装：在同一命令追加 --install（会创建 .venv 并访问依赖源）")
        return 0
    except ScaffoldError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
