#!/usr/bin/env python3
"""Reject staged new files outside the FILE_GRAPH placement contract."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from check_exemption_log import validate_exemptions  # noqa: E402


SKIP_MARKER = "[skip-file-placement]"
ROOT_WHITELIST = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".gitmessage",
    ".gitleaks.toml",
    ".markdownlint.json",
    ".markdownlintignore",
    ".pre-commit-config.yaml",
    ".spectral.yaml",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "STATUS.md",
    "SUPPORT.md",
    "commitlint.config.js",
    "dashboard.html",
    "importlinter.ini",
    "package-lock.json",
    "package.json",
    "pyproject.toml",
    "requirements-dev.txt",
}
FREE_TOP_AREAS = {
    ".claude",
    ".codex",
    ".github",
    "conventions",
    "meta",
    "scripts",
    "src",
    "tests",
    "worklogs",
}
DOCS_SUBSECTIONS = {"plan", "reports", "research", "specs", "templates", "历史文件"}


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def placement_error(relative: str) -> str | None:
    relative = relative.replace("\\", "/").strip("/")
    segments = relative.split("/") if relative else []
    if len(segments) == 1:
        return None if relative in ROOT_WHITELIST else f"根目录新增散文件「{relative}」"
    if not segments:
        return "空路径"
    if segments[0] in FREE_TOP_AREAS:
        return None
    if segments[0] == "docs":
        if len(segments) < 3:
            return f"docs/ 根下新增散文件「{relative}」"
        if segments[1] not in DOCS_SUBSECTIONS:
            return f"docs 子区 `{segments[1]}` 未在 FILE_GRAPH 登记"
        return None
    return f"顶层区 `{segments[0]}/` 未在 FILE_GRAPH 登记"


def _git(root: Path, *args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.returncode, result.stdout


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1 or not Path(args[0]).is_file():
        print("用法: python check_file_placement.py <commit_msg_file>", file=sys.stderr)
        return 1
    root = default_repo_root()
    message = Path(args[0]).read_text(encoding="utf-8")
    if SKIP_MARKER in message.lower():
        errors = validate_exemptions(message, root)
        if errors:
            print(f"FAIL 不可审计豁免: {'; '.join(errors)}", file=sys.stderr)
            return 1
        print("OK 已登记豁免")
        return 0
    code, output = _git(root, "diff", "--cached", "--name-only", "--diff-filter=A")
    if code != 0:
        print("FAIL 无法读取 Git 暂存区", file=sys.stderr)
        return 1
    errors = [
        error
        for line in output.splitlines()
        if line.strip()
        if (error := placement_error(line.strip()))
    ]
    if errors:
        print("FAIL 文件放置检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK 文件放置检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
