#!/usr/bin/env python3
"""Fail-closed checks shared by local hooks and CI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

CORE_FILES = (
    ".devguard.json",
    ".devguard-receipt.json",
    ".gitattributes",
    ".gitignore",
    ".pre-commit-config.yaml",
    ".github/workflows/devguard.yml",
    "README.md",
    "STATUS.md",
    "CLAUDE.md",
    "AGENTS.md",
    ".agents/skills/devguard/SKILL.md",
    ".agents/skills/devguard/agents/openai.yaml",
    ".codex/config.toml",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements-dev.txt",
    "conventions/README.md",
    "docs/plan/背景.md",
    "docs/plan/开发清单.md",
    "scripts/devguard.py",
    "scripts/install_hooks.py",
    "tests/governance/test_devguard.py",
    "worklogs/.gitkeep",
)
OPTIONAL_FILES = (
    ".github/CODEOWNERS",
    "docs/reports/.gitkeep",
    "docs/decisions/.gitkeep",
)
TEMPLATE_TOKEN = re.compile(r"\{\{[A-Z_]+\}\}")
CONVENTIONAL_COMMIT = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\([a-z0-9][a-z0-9._/-]*\))?!?: .{1,100}$"
)


def load_config(root: Path) -> tuple[dict[str, object] | None, list[str]]:
    path = root / ".devguard.json"
    if not path.is_file():
        return None, ["missing .devguard.json"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"invalid .devguard.json: {error}"]
    if not isinstance(data, dict):
        return None, [".devguard.json must contain an object"]
    return data, []


def local_hooks_path(root: Path) -> Path | None:
    result = subprocess.run(
        ["git", "config", "--local", "--path", "--get", "core.hooksPath"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    configured = Path(result.stdout.strip())
    return configured.resolve() if configured.is_absolute() else (root / configured).resolve()


def hook_exists(hooks: Path, hook_name: str) -> bool:
    return (hooks / hook_name).is_file() or (hooks / f"{hook_name}.exe").is_file()


def verify(root: Path, *, require_hooks: bool = False) -> list[str]:
    """Return every closure violation; success is represented only by ``[]``."""
    root = root.resolve()
    config, errors = load_config(root)
    if config is None:
        return errors
    profile = config.get("profile")
    if profile not in {"core", "optional"}:
        errors.append("profile must be 'core' or 'optional'")
        return errors

    required = CORE_FILES + (OPTIONAL_FILES if profile == "optional" else ())
    for relative_path in required:
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")

    for relative_path in (
        "README.md",
        "STATUS.md",
        "CLAUDE.md",
        "AGENTS.md",
        ".agents/skills/devguard/SKILL.md",
        "docs/plan/背景.md",
        "docs/plan/开发清单.md",
    ):
        path = root / relative_path
        if path.is_file() and TEMPLATE_TOKEN.search(path.read_text(encoding="utf-8")):
            errors.append(f"unresolved template token: {relative_path}")

    pre_commit = root / ".pre-commit-config.yaml"
    if pre_commit.is_file():
        text = pre_commit.read_text(encoding="utf-8")
        for required_text in (
            "default_install_hook_types: [pre-commit, commit-msg]",
            "id: devguard-verify",
            "stages: [commit-msg]",
            "id: ruff",
            "id: gitleaks",
        ):
            if required_text not in text:
                errors.append(f"pre-commit closure missing: {required_text}")

    workflow = root / ".github" / "workflows" / "devguard.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        for required_text in (
            "pip install -r requirements-dev.txt",
            "python scripts/devguard.py verify",
            "pre_commit run --all-files",
            "pytest tests/governance",
        ):
            if required_text not in text:
                errors.append(f"CI closure missing: {required_text}")

    requirements = root / "requirements-dev.txt"
    if requirements.is_file():
        declared = requirements.read_text(encoding="utf-8").lower()
        for package in ("pre-commit", "pytest", "ruff"):
            if not re.search(rf"(?m)^{re.escape(package)}==[^\s]+$", declared):
                errors.append(f"dependency not pinned: {package}")

    if require_hooks:
        if not (root / ".git").is_dir():
            errors.append("Git repository is not initialized")
        expected_hooks = (root / ".git" / "hooks").resolve()
        configured_hooks = local_hooks_path(root)
        if configured_hooks != expected_hooks:
            errors.append(
                "local core.hooksPath must point to .git/hooks so project hooks are active"
            )
        for hook_name in ("pre-commit", "commit-msg"):
            if not hook_exists(expected_hooks, hook_name):
                errors.append(f"required Git hook is not installed: {hook_name}")
    return errors


def validate_commit_message(path: Path) -> list[str]:
    if not path.is_file():
        return [f"commit message file does not exist: {path}"]
    first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not first_line:
        return ["commit message is empty"]
    subject = first_line[0].strip()
    if subject.startswith(("Merge ", "Revert ")):
        return []
    if not CONVENTIONAL_COMMIT.fullmatch(subject):
        return [
            "commit subject must use Conventional Commits, for example "
            "'fix(api): reject invalid ids'"
        ]
    return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DevGuard checks")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--root", type=Path, default=Path.cwd())
    verify_parser.add_argument("--require-hooks", action="store_true")
    commit_parser = subparsers.add_parser("commit-msg")
    commit_parser.add_argument("message_file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "verify":
        errors = verify(args.root, require_hooks=args.require_hooks)
    else:
        errors = validate_commit_message(args.message_file)
    if errors:
        print("DEVGUARD FAILED\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("DEVGUARD OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
