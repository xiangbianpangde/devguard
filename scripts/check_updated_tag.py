#!/usr/bin/env python3
"""Require staged managed Markdown documents to refresh ``> 更新:``."""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from check_exemption_log import validate_exemptions  # noqa: E402


SKIP_MARKER = "[skip-updated]"
EXCLUDE_PREFIXES = ("docs/templates/", "worklogs/", ".github/")
EXCLUDE_EXACT = {"CHANGELOG.md"}
UPDATE_TAG = re.compile(r"^>\s*更新[:：]\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def in_scope(relative: str) -> bool:
    relative = relative.replace("\\", "/")
    return bool(
        relative.endswith(".md")
        and relative not in EXCLUDE_EXACT
        and not relative.startswith(EXCLUDE_PREFIXES)
    )


def extract_update_date(content: str) -> str | None:
    match = UPDATE_TAG.search(content)
    return match.group(1) if match else None


def validate_update_tags(
    staged_files: list[str],
    read_staged: Callable[[str], str],
    today: str,
) -> list[str]:
    errors: list[str] = []
    for relative in staged_files:
        if not in_scope(relative):
            continue
        updated = extract_update_date(read_staged(relative))
        if updated is None:
            errors.append(f"{relative}: 缺 `> 更新: YYYY-MM-DD` 标签")
        elif updated != today:
            errors.append(f"{relative}: 更新日期 {updated} != 今天 {today}")
    return errors


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
        print("用法: python check_updated_tag.py <commit_msg_file>", file=sys.stderr)
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
    code, output = _git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if code != 0:
        print("FAIL 无法读取 Git 暂存区", file=sys.stderr)
        return 1
    files = [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]

    def read_staged(relative: str) -> str:
        read_code, text = _git(root, "show", f":{relative}")
        return text if read_code == 0 else ""

    errors = validate_update_tags(files, read_staged, dt.date.today().isoformat())
    if errors:
        print("FAIL 更新时间标签检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK 更新时间标签检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
