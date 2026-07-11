#!/usr/bin/env python3
"""Measure enforcement with real staged fault injections in temporary Git repos."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple


DEFAULT_THRESHOLD = 90.0


class Injection(NamedTuple):
    name: str
    gate_script: str
    mutation: str
    message: str
    expected_message: str
    apply: Callable[[Path], None]


class CaseResult(NamedTuple):
    name: str
    gate_script: str
    mutation: str
    expected_message: str
    blocked: bool
    return_code: int
    output: str


class EnforcementReport(NamedTuple):
    cases: tuple[CaseResult, ...]

    @property
    def blocked(self) -> int:
        return sum(case.blocked for case in self.cases)

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def rate(self) -> float:
        return 100.0 * self.blocked / self.total if self.total else 0.0


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _registry() -> str:
    markers = (
        ("[skip-worklog]", "check_worklog_ref.py"),
        ("[skip-status]", "check_status_updated.py"),
        ("[skip-worklog-structure]", "check_worklog_structure.py"),
        ("[skip-file-placement]", "check_file_placement.py"),
        ("[skip-updated]", "check_updated_tag.py"),
        ("[skip-docsync]", "check_doc_sync.py"),
        ("[skip-gate]", "check_convergence_gate.py"),
    )
    catalog = "\n".join(f"| `{marker}` | {gate} | emergency only |" for marker, gate in markers)
    return (
        "## 二、已登记豁免标记\n\n"
        "| 豁免标记 | 钩子 | 说明 |\n|---|---|---|\n"
        f"{catalog}\n\n"
        "## 三、豁免使用记录\n\n"
        "| 日期 | 范围 | 钩子 | 豁免标记 | 申请人 | 为何 |\n"
        "|---|---|---|---|---|---|\n"
    )


def _seed_repository(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if _git(root, "init", "-q").returncode != 0:
        raise RuntimeError("git init failed")
    empty_hooks = root / ".git" / "devguard-empty-hooks"
    empty_hooks.mkdir(parents=True, exist_ok=True)
    hook_isolation = _git(
        root,
        "config",
        "core.hooksPath",
        ".git/devguard-empty-hooks",
    )
    if hook_isolation.returncode != 0:
        raise RuntimeError(f"global Git hook isolation failed: {hook_isolation.stderr}")
    _git(root, "config", "user.email", "fault-injection@example.invalid")
    _git(root, "config", "user.name", "DevGuard Fault Injection")
    today = dt.date.today().isoformat()
    progress = "<!-- devguard-progress: completed=1 total=3 -->"
    _write(root, "README.md", "seed\n")
    _write(
        root,
        "STATUS.md",
        f"> 更新: {today}\n{progress}\n"
        "<!-- convergence-gate: nodes=2 last_converged_fp=1 -->\n"
        "| #1 seed | ✅ |\n",
    )
    _write(
        root,
        "docs/plan/开发清单.md",
        f"> 更新: {today}\n{progress}\n"
        "| 1 | seed | ✅ |\n| 2 | node | ⏳ |\n| 3 | next | ⏳ |\n",
    )
    _write(root, "CLAUDE.md", f"> 更新: {today}\n{progress}\n")
    _write(root, "docs/specs/seed.md", f"> 更新: {today}\n# seed\n")
    _write(root, "meta/豁免清单.md", _registry())
    _write(root, "meta/FILE_GRAPH.md", "# FILE_GRAPH\n")
    _git(root, "add", ".")
    committed = _git(root, "commit", "-qm", "chore: seed")
    if committed.returncode != 0:
        raise RuntimeError(f"seed commit failed: {committed.stderr}")


def _valid_worklog() -> str:
    return (
        "# log\n## 做了什么\n- [x] completed\n"
        "## 验证结果\n- command exit 0\n## 下一步\n- handoff\n"
    )


def _injections() -> tuple[Injection, ...]:
    def change_readme(root: Path) -> None:
        _write(root, "README.md", "changed\n")
        _git(root, "add", "README.md")

    def malformed_worklog(root: Path) -> None:
        _write(root, "worklogs/2026-07-10_bad.md", "# narrative only\n")
        _git(root, "add", "worklogs/2026-07-10_bad.md")

    def valid_worklog_only(root: Path) -> None:
        _write(root, "worklogs/2026-07-10_good.md", _valid_worklog())
        _git(root, "add", "worklogs/2026-07-10_good.md")

    def root_stray(root: Path) -> None:
        _write(root, "scratch.md", "unclassified\n")
        _git(root, "add", "scratch.md")

    def unregistered_usage(root: Path) -> None:
        path = root / "meta" / "豁免清单.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "| 2026-07-10 | test | fake.py | `[skip-invented]` | owner | test |\n",
            encoding="utf-8",
        )
        _git(root, "add", "meta/豁免清单.md")

    def stale_tag(root: Path) -> None:
        _write(root, "docs/specs/seed.md", "> 更新: 2000-01-01\n# changed\n")
        _git(root, "add", "docs/specs/seed.md")

    def status_only_feature(root: Path) -> None:
        status = (root / "STATUS.md").read_text(encoding="utf-8")
        # The seeded plan already declares #1-#3. Add a truly status-only #4 so
        # the intended document-sync failure is what blocks the mutation.
        _write(root, "STATUS.md", status + "| #4 status-only | ✅ |\n")
        _git(root, "add", "STATUS.md")

    def cross_convergence_node(root: Path) -> None:
        plan = (root / "docs/plan/开发清单.md").read_text(encoding="utf-8")
        plan = plan.replace("| 2 | node | ⏳ |", "| 2 | node | ✅ |")
        plan = plan.replace("| 3 | next | ⏳ |", "| 3 | next | ✅ |")
        _write(root, "docs/plan/开发清单.md", plan)
        _git(root, "add", "docs/plan/开发清单.md")

    return (
        Injection(
            "missing-worklog-reference",
            "check_worklog_ref.py",
            "stage a change but omit the mandatory worklog reference",
            "feat: changed without worklog",
            "必须引用",
            change_readme,
        ),
        Injection(
            "phantom-worklog-reference",
            "check_worklog_ref.py",
            "reference a worklog path that has no staged blob",
            "feat: x worklogs/2026-07-10_phantom.md",
            "暂存",
            change_readme,
        ),
        Injection(
            "unaudited-worklog-skip",
            "check_worklog_ref.py",
            "use [skip-worklog] without a newly staged registry record",
            "hotfix: x [skip-worklog]",
            "豁免",
            change_readme,
        ),
        Injection(
            "malformed-worklog",
            "check_worklog_structure.py",
            "stage a narrative-only worklog without required evidence sections",
            "feat: x worklogs/2026-07-10_bad.md",
            "缺必需段",
            malformed_worklog,
        ),
        Injection(
            "worklog-status-desync",
            "check_status_updated.py",
            "stage a worklog without staging STATUS.md",
            "feat: x worklogs/2026-07-10_good.md",
            "STATUS.md",
            valid_worklog_only,
        ),
        Injection(
            "root-file-placement",
            "check_file_placement.py",
            "stage an unclassified root-level file",
            "chore: add scratch",
            "根目录",
            root_stray,
        ),
        Injection(
            "unregistered-exemption",
            "check_exemption_log.py",
            "stage a usage row for a marker absent from the exemption catalog",
            "fix: x [skip-invented]",
            "未登记",
            unregistered_usage,
        ),
        Injection(
            "stale-update-tag",
            "check_updated_tag.py",
            "stage a managed document with a stale update date",
            "docs: stale tag",
            "更新日期",
            stale_tag,
        ),
        Injection(
            "status-plan-structure-drift",
            "check_doc_sync.py",
            "add a numbered STATUS feature without its plan projection",
            "docs: add status-only feature",
            "开发清单",
            status_only_feature,
        ),
        Injection(
            "unconverged-node-crossing",
            "check_convergence_gate.py",
            "mark work beyond pending convergence node #2 as delivered",
            "feat: cross convergence node",
            "越过",
            cross_convergence_node,
        ),
    )


def _run_case(script_root: Path, root: Path, injection: Injection) -> CaseResult:
    injection.apply(root)
    message_file = root / "COMMIT_EDITMSG"
    message_file.write_text(injection.message + "\n", encoding="utf-8")
    environment = os.environ.copy()
    environment["DEVGUARD_REPO_ROOT"] = str(root)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        [
            sys.executable,
            str(script_root / "scripts" / injection.gate_script),
            str(message_file),
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    blocked = completed.returncode != 0 and injection.expected_message in output
    return CaseResult(
        injection.name,
        injection.gate_script,
        injection.mutation,
        injection.expected_message,
        blocked,
        completed.returncode,
        output,
    )


def run_matrix(script_root: Path) -> EnforcementReport:
    script_root = script_root.resolve()
    results: list[CaseResult] = []
    with tempfile.TemporaryDirectory(prefix="devguard-enforcement-") as temporary:
        base = Path(temporary)
        for index, injection in enumerate(_injections(), start=1):
            root = base / f"case-{index:02d}"
            _seed_repository(root)
            results.append(_run_case(script_root, root, injection))
    return EnforcementReport(tuple(results))


def format_report(report: EnforcementReport, threshold: float = DEFAULT_THRESHOLD) -> str:
    lines = ["=== 强制性故障注入矩阵 ==="]
    for case in report.cases:
        state = "BLOCKED" if case.blocked else "MISSED"
        lines.append(
            f"[{state}] {case.name} | gate={case.gate_script} | mutation={case.mutation} "
            f"| expect={case.expected_message!r} | exit={case.return_code}"
        )
        if not case.blocked and case.output:
            lines.append(f"  output: {case.output.splitlines()[-1]}")
    lines.append(
        f"强制性拦截率: {report.blocked}/{report.total} = {report.rate:.1f}% "
        f"(阈值 {threshold:.1f}%)"
    )
    lines.append("OK 强制性达标" if report.rate >= threshold else "FAIL 强制性未达标")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    report = run_matrix(args.repo_root)
    print(format_report(report, args.threshold))
    return 0 if report.rate >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
