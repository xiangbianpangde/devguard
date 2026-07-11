#!/usr/bin/env python3
"""Require commit messages to reference a real worklog in the staged change."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from check_exemption_log import validate_exemptions  # noqa: E402


WORKLOG_PATTERN = re.compile(
    r"(?<![\w/])worklogs[\\/]+(?!decisions[\\/])"
    r"\d{4}-\d{2}-\d{2}[_-][^\s)\]}>]+\.md",
    re.IGNORECASE,
)
SKIP_MARKER = "[skip-worklog]"


def default_repo_root() -> Path:
    configured = os.environ.get("DEVGUARD_REPO_ROOT")
    return (
        Path(configured).resolve()
        if configured
        else Path(__file__).resolve().parents[1]
    )


def referenced_worklogs(message: str) -> set[str]:
    return {
        match.group(0).replace("\\", "/") for match in WORKLOG_PATTERN.finditer(message)
    }


def staged_changed_files(root: Path) -> set[str] | None:
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMR",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return None
    return {
        line.strip().replace("\\", "/")
        for line in completed.stdout.splitlines()
        if line.strip()
    }


def _staged_blob_exists(root: Path, relative: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f":{relative}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def validate_worklog_reference(
    message: str, repo_root: Path | None = None
) -> list[str]:
    root = (repo_root or default_repo_root()).resolve()
    if SKIP_MARKER in message.lower():
        errors = validate_exemptions(message, root)
        return [f"豁免不可审计: {error}" for error in errors]

    references = referenced_worklogs(message)
    if not references:
        return ["commit message 必须引用 worklogs/YYYY-MM-DD_<描述>.md"]
    staged = staged_changed_files(root)
    if staged is None:
        return ["无法读取 Git 暂存区，worklog 检查按 fail-closed 拒绝"]
    missing = sorted(
        reference
        for reference in references
        if reference not in staged or not _staged_blob_exists(root, reference)
    )
    if missing:
        return [f"引用的 worklog 未作为真实文件出现在本次暂存变更: {missing}"]
    return []


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("用法: python check_worklog_ref.py <commit_msg_file>", file=sys.stderr)
        return 1
    message_file = Path(args[0])
    if not message_file.is_file():
        print(f"FAIL commit message 文件不存在: {message_file}", file=sys.stderr)
        return 1
    errors = validate_worklog_reference(message_file.read_text(encoding="utf-8"))
    if errors:
        print("FAIL worklog 引用检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK worklog 引用检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
