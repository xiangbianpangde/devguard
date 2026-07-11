#!/usr/bin/env python3
"""Install project hooks without discarding an existing global hook policy."""

from __future__ import annotations

import argparse
import os
import shlex
import stat
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

COMPOSED_MARKER = "# DevGuard composed hook"


class HookInstallError(RuntimeError):
    """Raised when the combined hook chain cannot be installed safely."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _path_value(root: Path, *config_args: str) -> Path | None:
    result = _git(root, "config", *config_args)
    if result.returncode == 1 or not result.stdout.strip():
        return None
    if result.returncode != 0:
        raise HookInstallError(
            f"git config {' '.join(config_args)} failed: {result.stderr.strip()}"
        )
    configured = Path(result.stdout.strip()).expanduser()
    return (
        configured.resolve()
        if configured.is_absolute()
        else (root / configured).resolve()
    )


def _effective_external_hooks_path(root: Path) -> Path | None:
    local_hooks = (root / ".git" / "hooks").resolve()
    stored = _path_value(
        root,
        "--local",
        "--path",
        "--get",
        "devguard.externalHooksPath",
    )
    global_hooks = _path_value(
        root,
        "--global",
        "--path",
        "--get",
        "core.hooksPath",
    )
    effective = _path_value(root, "--path", "--get", "core.hooksPath")
    for candidate in (global_hooks, stored, effective):
        if candidate is not None and candidate != local_hooks:
            return candidate
    return None


def _isolated_git_config_environment(root: Path) -> dict[str, str]:
    empty_config = root / ".git" / "devguard-empty-gitconfig"
    empty_config.write_text("", encoding="utf-8", newline="\n")
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": str(empty_config),
        "GIT_CONFIG_SYSTEM": str(empty_config),
    }


def _write_hook_wrapper(path: Path, commands: Sequence[str]) -> None:
    content = (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"{COMPOSED_MARKER}\n" + "\n".join(commands) + "\n"
    )
    path.write_text(content, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _reset_composed_hooks(root: Path) -> None:
    hooks = root / ".git" / "hooks"
    wrapper = hooks / "pre-commit"
    devguard = hooks / "pre-commit.devguard"
    if devguard.is_file():
        if wrapper.is_file():
            wrapper.unlink()
        devguard.replace(wrapper)
    pre_push = hooks / "pre-push"
    if pre_push.is_file():
        text = pre_push.read_text(encoding="utf-8", errors="replace")
        if COMPOSED_MARKER in text:
            pre_push.unlink()


def _chain_external_hooks(root: Path, external_hooks: Path) -> None:
    external_hooks = external_hooks.resolve()
    local_hooks = (root / ".git" / "hooks").resolve()
    if not external_hooks.is_dir() or external_hooks == local_hooks:
        return
    local_hooks.mkdir(parents=True, exist_ok=True)
    for hook_name in ("pre-commit", "pre-push"):
        external_hook = external_hooks / hook_name
        if not external_hook.is_file():
            continue
        local_hook = local_hooks / hook_name
        commands = [f'{shlex.quote(external_hook.as_posix())} "$@"']
        if local_hook.is_file():
            devguard_hook = local_hooks / f"{hook_name}.devguard"
            if devguard_hook.exists():
                raise HookInstallError(
                    f"refusing to overwrite hook chain: {devguard_hook}"
                )
            local_hook.replace(devguard_hook)
            commands.append(f'exec {shlex.quote(devguard_hook.as_posix())} "$@"')
        else:
            commands[0] = f"exec {commands[0]}"
        _write_hook_wrapper(local_hook, commands)


def _unset_local_hooks_path(root: Path) -> None:
    if _path_value(root, "--local", "--path", "--get", "core.hooksPath") is None:
        return
    result = _git(root, "config", "--local", "--unset-all", "core.hooksPath")
    if result.returncode != 0:
        raise HookInstallError(f"cannot unset local core.hooksPath: {result.stderr}")


def install_hooks(root: Path) -> Path:
    root = root.resolve()
    if not (root / ".git").is_dir():
        raise HookInstallError(f"Git repository is not initialized: {root}")
    external_hooks = _effective_external_hooks_path(root)
    _reset_composed_hooks(root)
    _unset_local_hooks_path(root)
    environment = _isolated_git_config_environment(root)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pre_commit",
            "install",
            "--hook-type",
            "pre-commit",
            "--hook-type",
            "commit-msg",
        ],
        cwd=root,
        env=environment,
        check=False,
    )
    if result.returncode != 0:
        raise HookInstallError(
            f"pre-commit hook installation failed: exit={result.returncode}"
        )
    if external_hooks is not None:
        _chain_external_hooks(root, external_hooks)
    local_hooks = (root / ".git" / "hooks").resolve()
    configured = _git(
        root,
        "config",
        "--local",
        "core.hooksPath",
        local_hooks.as_posix(),
    )
    if configured.returncode != 0:
        raise HookInstallError(f"cannot activate local hooks: {configured.stderr}")
    if external_hooks is not None and external_hooks.is_dir():
        stored = _git(
            root,
            "config",
            "--local",
            "devguard.externalHooksPath",
            external_hooks.as_posix(),
        )
        if stored.returncode != 0:
            raise HookInstallError(f"cannot record external hooks: {stored.stderr}")
    return local_hooks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        hooks = install_hooks(args.root)
    except HookInstallError as error:
        print(f"HOOK INSTALL FAILED: {error}", file=sys.stderr)
        return 1
    print(f"HOOK INSTALL OK: {hooks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
