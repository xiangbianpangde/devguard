#!/usr/bin/env python3
"""Require every ``[skip-*]`` exemption to be registered and auditable."""

from __future__ import annotations

import argparse
import collections
import os
import re
import subprocess
import sys
from pathlib import Path


REGISTRY_REL = "meta/豁免清单.md"
SKIP_MARKER = re.compile(r"\[skip-[a-z0-9-]+\]", re.IGNORECASE)
CATALOG_HEADING = re.compile(r"^##\s+二[、.]", re.MULTILINE)
USAGE_HEADING = re.compile(r"^##\s+三[、.]", re.MULTILINE)


def default_repo_root() -> Path:
    configured = os.environ.get("DEVGUARD_REPO_ROOT")
    return (
        Path(configured).resolve()
        if configured
        else Path(__file__).resolve().parents[1]
    )


def extract_skip_markers(message: str) -> set[str]:
    return {marker.lower() for marker in SKIP_MARKER.findall(message)}


def _section(
    text: str, heading: re.Pattern[str], next_heading: re.Pattern[str] | None
) -> str:
    start = heading.search(text)
    if not start:
        return ""
    tail = text[start.end() :]
    if next_heading and (end := next_heading.search(tail)):
        tail = tail[: end.start()]
    return tail


def registry_markers(text: str) -> set[str]:
    """Return catalog markers only; prose and usage rows do not register markers."""
    catalog = _section(text, CATALOG_HEADING, USAGE_HEADING)
    markers: set[str] = set()
    for line in catalog.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [
            cell.strip().strip("`").lower()
            for cell in line.strip().strip("|").split("|")
        ]
        if cells and re.fullmatch(r"\[skip-[a-z0-9-]+\]", cells[0]):
            markers.add(cells[0])
    return markers


def usage_counts(text: str) -> collections.Counter[str]:
    """Count markers in complete six-column usage rows."""
    usage = _section(text, USAGE_HEADING, None)
    counts: collections.Counter[str] = collections.Counter()
    for line in usage.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6 or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        # A record is auditable only when date, scope, hook, owner and reason are non-empty.
        if not all(cells[index].strip(" `") for index in (0, 1, 2, 4, 5)):
            continue
        for marker in extract_skip_markers(cells[3]):
            counts[marker] += 1
    return counts


def _git(root: Path, *args: str) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return completed.returncode, completed.stdout


def _git_text(root: Path, ref: str) -> str:
    return_code, output = _git(root, "show", ref)
    return output if return_code == 0 else ""


def _staged_files(root: Path) -> set[str] | None:
    return_code, output = _git(root, "diff", "--cached", "--name-only")
    if return_code != 0:
        return None
    return {
        line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()
    }


def validate_exemptions(message: str, repo_root: Path | None = None) -> list[str]:
    root = (repo_root or default_repo_root()).resolve()
    markers = extract_skip_markers(message)
    if not markers:
        return []

    staged_files = _staged_files(root)
    if staged_files is None:
        return ["无法读取 Git 暂存区，豁免检查按 fail-closed 拒绝"]
    if REGISTRY_REL not in staged_files:
        return [f"豁免必须同步暂存 {REGISTRY_REL} 并新增使用记录"]

    staged = _git_text(root, f":{REGISTRY_REL}")
    if not staged:
        return [f"无法读取暂存版 {REGISTRY_REL}"]
    registered = registry_markers(staged)
    unregistered = markers - registered
    errors: list[str] = []
    if unregistered:
        errors.append(f"使用了未登记的豁免标记: {sorted(unregistered)}")

    head = _git_text(root, f"HEAD:{REGISTRY_REL}")
    before = usage_counts(head)
    after = usage_counts(staged)
    missing_records = sorted(
        marker for marker in markers if after[marker] <= before[marker]
    )
    if missing_records:
        errors.append(f"本次暂存未为这些豁免新增完整使用记录: {missing_records}")
    return errors


def audit(repo_root: Path) -> int:
    return_code, history = _git(repo_root, "log", "--format=%B")
    if return_code != 0:
        print("FAIL 无法读取 Git 历史", file=sys.stderr)
        return 1
    registry = (repo_root / REGISTRY_REL).read_text(encoding="utf-8")
    used = extract_skip_markers(history)
    missing = used - registry_markers(registry)
    print(f"历史豁免标记: {sorted(used)}")
    print(f"未登记标记: {sorted(missing)}")
    return 1 if missing else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("commit_msg_file", nargs="?", type=Path)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    args = parser.parse_args(argv)
    if args.audit:
        return audit(args.repo_root.resolve())
    if args.commit_msg_file is None or not args.commit_msg_file.is_file():
        print("FAIL: 必须提供存在的 commit message 文件", file=sys.stderr)
        return 1
    errors = validate_exemptions(
        args.commit_msg_file.read_text(encoding="utf-8"), args.repo_root
    )
    if errors:
        print("FAIL 豁免登记检查不通过：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK 豁免登记检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
