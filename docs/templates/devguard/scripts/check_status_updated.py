#!/usr/bin/env python3
"""Keep staged top-level worklogs synchronized with STATUS.md."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

# Windows 中文 stdout 兼容（cp1252 下打印中文会 UnicodeEncodeError）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from check_exemption_log import validate_exemptions  # noqa: E402


STATUS_REL = "STATUS.md"
SKIP_MARKER = "[skip-status]"
WORKLOG_RE = re.compile(r"^worklogs/(\d{4}-\d{2}-\d{2})[_-].+\.md$", re.IGNORECASE)
STATUS_DATE_RE = re.compile(r"^>\s*更新[:：]\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def validate_status_sync(
    staged_files: set[str],
    read_staged: Callable[[str], str],
) -> list[str]:
    worklog_dates = sorted(
        match.group(1)
        for relative in staged_files
        if (match := WORKLOG_RE.match(relative.replace("\\", "/")))
    )
    # R5-10（2026-08-14 红队第六轮）：STATUS 独占更新不强制 worklog——
    # 进度数据源的任何实质变更须有支撑记录（worklog 或收束报告/收束产物）。
    if STATUS_REL in staged_files and not worklog_dates:
        has_report_support = any(
            rel.startswith("docs/reports/") or "worklogs/decisions/" in rel for rel in staged_files
        )
        if not has_report_support:
            return [
                "STATUS.md 变更必须同步 worklog（或 docs/reports/ 收束产物）——进度数据源需支撑记录"
            ]
    if not worklog_dates:
        return []
    if STATUS_REL not in staged_files:
        return ["修改 worklog 时必须同步暂存 STATUS.md"]
    match = STATUS_DATE_RE.search(read_staged(STATUS_REL))
    if not match:
        return ["STATUS.md 缺 `> 更新: YYYY-MM-DD` 标签"]
    latest = worklog_dates[-1]
    if match.group(1) != latest:
        return [f"STATUS.md 更新日期 {match.group(1)} 与最新 worklog {latest} 不一致"]
    return []


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
        print("用法: python check_status_updated.py <commit_msg_file>", file=sys.stderr)
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
    return_code, output = _git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if return_code != 0:
        print("FAIL 无法读取 Git 暂存区", file=sys.stderr)
        return 1
    staged = {line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()}

    def read_staged(relative: str) -> str:
        code, text = _git(root, "show", f":{relative}")
        return text if code == 0 else ""

    errors = validate_status_sync(staged, read_staged)
    if errors:
        print("FAIL worklog/STATUS 同步检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK worklog/STATUS 同步检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
