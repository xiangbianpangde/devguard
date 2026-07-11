#!/usr/bin/env python3
"""Validate evidence-bearing structure of staged top-level worklogs."""

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


SKIP_MARKER = "[skip-worklog-structure]"
WORKLOG_RE = re.compile(r"^worklogs/\d{4}-\d{2}-\d{2}[_-].+\.md$", re.IGNORECASE)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[[xX]\]\s+\S", re.MULTILINE)
REQUIRED_SECTIONS = {
    "完成内容": ("做了什么", "完成了什么", "完成内容"),
    "验证结果": ("验证结果", "验证"),
    "交接/下一步": ("下一步", "交接", "给下一位"),
}
RECOMMENDED_SECTIONS = {
    "关键决策": ("关键决策",),
    "遇到的问题": ("遇到的问题",),
}


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def check_content(relative: str, content: str) -> tuple[list[str], list[str]]:
    headings = "\n".join(
        line.strip() for line in content.splitlines() if re.match(r"^\s*#{1,6}\s+", line)
    )
    errors = [
        f"{relative}: 缺必需段「{label}」"
        for label, alternatives in REQUIRED_SECTIONS.items()
        if not any(value in headings for value in alternatives)
    ]
    if not CHECKBOX_RE.search(content):
        errors.append(f"{relative}: 缺至少一个 `- [x]` 已完成项")
    warnings = [
        f"{relative}: 建议补充「{label}」"
        for label, alternatives in RECOMMENDED_SECTIONS.items()
        if not any(value in headings for value in alternatives)
    ]
    return errors, warnings


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
        print("用法: python check_worklog_structure.py <commit_msg_file>", file=sys.stderr)
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
    worklogs = [
        line.strip().replace("\\", "/")
        for line in output.splitlines()
        if WORKLOG_RE.match(line.strip().replace("\\", "/"))
    ]
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for relative in worklogs:
        read_code, content = _git(root, "show", f":{relative}")
        if read_code != 0:
            all_errors.append(f"{relative}: 无法读取暂存内容")
            continue
        errors, warnings = check_content(relative, content)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    for warning in all_warnings:
        print(f"WARN {warning}")
    if all_errors:
        print("FAIL worklog 结构检查不通过：", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK worklog 结构检查通过 ({len(worklogs)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
