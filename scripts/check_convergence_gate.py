#!/usr/bin/env python3
"""Block delivery beyond an unconverged, predeclared feature-point node."""

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
SKIP_MARKER = "[skip-gate]"
MARKER = re.compile(
    r"<!--\s*convergence-gate:\s*nodes=([\d,\s]+?)\s+last_converged_fp=(\d+)\s*-->"
)


def default_repo_root() -> Path:
    value = os.environ.get("DEVGUARD_REPO_ROOT")
    return Path(value).resolve() if value else Path(__file__).resolve().parents[1]


def parse_marker(text: str) -> tuple[list[int], int] | None:
    match = MARKER.search(text)
    if not match:
        return None
    nodes = sorted(
        {int(value.strip()) for value in match.group(1).split(",") if value.strip()}
    )
    last = int(match.group(2))
    if not nodes or any(node <= 0 for node in nodes) or last < 0:
        return None
    return nodes, last


def max_done_fp(plan_text: str) -> int:
    maximum = 0
    for line in plan_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip().strip("*") for cell in line.strip().strip("|").split("|")]
        if (
            cells
            and cells[0].lstrip("#").isdigit()
            and any("✅" in cell for cell in cells)
        ):
            maximum = max(maximum, int(cells[0].lstrip("#")))
    return maximum


def evaluate_gate(status_text: str, head_plan: str, staged_plan: str) -> list[str]:
    parsed = parse_marker(status_text)
    if parsed is None:
        return ["STATUS.md 缺有效 convergence-gate 标记，闸门按 fail-closed 拒绝"]
    nodes, last_converged = parsed
    pending = [node for node in nodes if node > last_converged]
    if not pending:
        return []
    next_node = min(pending)
    before = max_done_fp(head_plan)
    after = max_done_fp(staged_plan)
    if after > next_node and after > before:
        return [
            f"交付功能点 #{after} 越过未收束节点 #{next_node} "
            f"(last_converged_fp={last_converged})"
        ]
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


def _show(root: Path, ref: str) -> str:
    code, text = _git(root, "show", ref)
    return text if code == 0 else ""


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1 or not Path(args[0]).is_file():
        print(
            "用法: python check_convergence_gate.py <commit_msg_file>", file=sys.stderr
        )
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
    status = _show(root, f":{STATUS_REL}") or _show(root, f"HEAD:{STATUS_REL}")
    head_plan = _show(root, f"HEAD:{PLAN_REL}")
    staged_plan = _show(root, f":{PLAN_REL}") or head_plan
    errors = evaluate_gate(status, head_plan, staged_plan)
    if errors:
        print("FAIL 收束闸门拦截：", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK 收束闸门通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
