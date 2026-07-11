#!/usr/bin/env python3
"""Keep structural feature-point changes synchronized across project records."""

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


STATUS_REL = "STATUS.md"
PLAN_REL = "docs/plan/开发清单.md"
AI_CONTEXT_REL = "CLAUDE.md"
SKIP_MARKER = "[skip-docsync]"
STATUS_FP_RE = re.compile(r"^\|\s*\*{0,2}#?(\d+)\b")
PLAN_FP_RE = re.compile(r"^\|\s*\*{0,2}#?(\d+)\s*\|")


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def status_fps(text: str) -> set[int]:
    return {
        int(match.group(1))
        for line in text.splitlines()
        if (match := STATUS_FP_RE.match(line.strip()))
    }


def plan_fps(text: str) -> set[int]:
    return {
        int(match.group(1))
        for line in text.splitlines()
        if (match := PLAN_FP_RE.match(line.strip()))
    }


def sync_errors(
    status_head: set[int],
    status_staged: set[int],
    plan_head: set[int],
    plan_staged: set[int],
    ai_context_staged: bool,
) -> tuple[list[str], bool]:
    added_status = status_staged - status_head
    removed_status = status_head - status_staged
    added_plan = plan_staged - plan_head
    removed_plan = plan_head - plan_staged
    structural = bool(added_status or removed_status or added_plan or removed_plan)
    errors: list[str] = []
    if missing := sorted(added_status - plan_staged):
        errors.append(f"STATUS 新增 {missing}，开发清单暂存版缺对应功能点")
    if missing := sorted(added_plan - status_staged):
        errors.append(f"开发清单新增 {missing}，STATUS 暂存版缺对应功能点")
    if lingering := sorted(removed_status & plan_staged):
        errors.append(f"STATUS 删除 {lingering}，开发清单仍保留")
    if lingering := sorted(removed_plan & status_staged):
        errors.append(f"开发清单删除 {lingering}，STATUS 仍保留")
    if structural and not ai_context_staged:
        errors.append("结构性功能点改动必须同步暂存 AI 上下文 CLAUDE.md")
    return errors, structural


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


def _content(root: Path, relative: str, staged: bool) -> str:
    code, text = _git(root, "show", f":{relative}" if staged else f"HEAD:{relative}")
    return text if code == 0 else ""


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1 or not Path(args[0]).is_file():
        print("用法: python check_doc_sync.py <commit_msg_file>", file=sys.stderr)
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
    staged = {
        line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()
    }
    if not ({STATUS_REL, PLAN_REL} & staged):
        return 0
    status_head = status_fps(_content(root, STATUS_REL, staged=False))
    status_after = status_fps(
        _content(root, STATUS_REL, staged=True)
        if STATUS_REL in staged
        else _content(root, STATUS_REL, staged=False)
    )
    plan_head = plan_fps(_content(root, PLAN_REL, staged=False))
    plan_after = plan_fps(
        _content(root, PLAN_REL, staged=True)
        if PLAN_REL in staged
        else _content(root, PLAN_REL, staged=False)
    )
    errors, structural = sync_errors(
        status_head,
        status_after,
        plan_head,
        plan_after,
        AI_CONTEXT_REL in staged,
    )
    if errors:
        print("FAIL 文档同步检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    if STATUS_REL in staged and not structural and PLAN_REL not in staged:
        print("WARN STATUS 值级改动未同步开发清单")
    print("OK 文档同步检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
