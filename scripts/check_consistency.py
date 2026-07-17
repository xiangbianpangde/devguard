#!/usr/bin/env python3
"""Measure repository consistency from executable and cross-file facts.

The score is deliberately not an inventory score.  A file earns no credit merely
for existing: projections must agree, convention/spec links must be reciprocal,
generated metadata must reproduce cleanly, configured hooks must bind to real
gate scripts, and the fault-injection matrix must actually block bad changes.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import yaml


DEFAULT_THRESHOLD = 80.0
PROGRESS_MARKER = re.compile(r"<!--\s*devguard-progress:\s*completed=(\d+)\s+total=(\d+)\s*-->")
CONVENTION_IDS = (
    "01-architecture",
    "02-coding",
    "03-git",
    "04-api",
    "05-testing",
    "06-documentation",
    "08-code-understanding",
)
REQUIRED_GATE_SCRIPTS = (
    "check_worklog_ref.py",
    "check_status_updated.py",
    "check_worklog_structure.py",
    "check_file_placement.py",
    "check_exemption_log.py",
    "check_updated_tag.py",
    "check_doc_sync.py",
    "check_convergence_gate.py",
)


class Fact(NamedTuple):
    name: str
    passed: bool
    detail: str


class Dimension(NamedTuple):
    name: str
    facts: tuple[Fact, ...]

    @property
    def passed(self) -> int:
        return sum(fact.passed for fact in self.facts)

    @property
    def total(self) -> int:
        return len(self.facts)


class ConsistencyReport(NamedTuple):
    dimensions: tuple[Dimension, ...]

    @property
    def passed(self) -> int:
        return sum(dimension.passed for dimension in self.dimensions)

    @property
    def total(self) -> int:
        return sum(dimension.total for dimension in self.dimensions)

    @property
    def score(self) -> float:
        return 100.0 * self.passed / self.total if self.total else 0.0


CommandRunner = Callable[[list[str]], tuple[int, str]]


def _read(root: Path, relative: str) -> str | None:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeError):
        return None


def _progress(text: str | None) -> tuple[int, int] | None:
    if text is None:
        return None
    match = PROGRESS_MARKER.search(text)
    if not match:
        return None
    completed, total = (int(value) for value in match.groups())
    if total <= 0 or completed < 0 or completed > total:
        return None
    return completed, total


def _feature_ids(text: str | None) -> set[int]:
    """Extract table rows whose first cell is exactly a numeric feature id."""
    if text is None:
        return set()
    pattern = re.compile(r"^\|\s*\*{0,2}#?(\d+)\*{0,2}\s*\|", re.MULTILINE)
    return {int(match.group(1)) for match in pattern.finditer(text)}


def evaluate_progress_truth(root: Path) -> Dimension:
    """Check STATUS as truth and its plan/AI-context projections."""
    status = _progress(_read(root, "STATUS.md"))
    facts = [
        Fact(
            "STATUS marker",
            status is not None,
            "STATUS.md has a valid devguard-progress marker"
            if status
            else "STATUS.md 缺有效 devguard-progress 标记",
        )
    ]
    for label, relative in (
        ("开发清单", "docs/plan/开发清单.md"),
        ("CLAUDE", "CLAUDE.md"),
    ):
        projection = _progress(_read(root, relative))
        passed = status is not None and projection == status
        facts.append(
            Fact(
                f"{label} projection",
                passed,
                f"{relative}: {projection!r}, STATUS: {status!r}",
            )
        )
    expected_ids = set(range(1, status[1] + 1)) if status else set()
    for label, relative in (
        ("STATUS详细表", "STATUS.md"),
        ("开发清单详细表", "docs/plan/开发清单.md"),
    ):
        actual_ids = _feature_ids(_read(root, relative))
        passed = bool(expected_ids) and actual_ids == expected_ids
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        facts.append(
            Fact(
                f"{label} continuity",
                passed,
                (
                    f"rows={len(actual_ids)}/{len(expected_ids)} "
                    f"missing={missing[:5]} extra={extra[:5]}"
                ),
            )
        )
    return Dimension("进度真源", tuple(facts))


def evaluate_spec_contract(root: Path) -> Dimension:
    """Check reciprocal links for every core convention/spec pair."""
    facts: list[Fact] = []
    for convention_id in CONVENTION_IDS:
        matches = sorted((root / "conventions").glob(f"{convention_id}_*.md"))
        convention = matches[0] if len(matches) == 1 else None
        spec = root / "docs" / "specs" / f"{convention_id}.md"
        convention_text = (
            convention.read_text(encoding="utf-8") if convention and convention.is_file() else ""
        )
        spec_text = spec.read_text(encoding="utf-8") if spec.is_file() else ""
        reciprocal = bool(
            convention
            and spec.is_file()
            and spec.name in convention_text
            and convention.name in spec_text
        )
        facts.append(
            Fact(
                convention_id,
                reciprocal,
                "规范与 BDD 双向引用一致" if reciprocal else "规范/BDD 缺失、重名或未双向引用",
            )
        )
    return Dimension("规范-BDD契约", tuple(facts))


def _local_hooks(config: object) -> list[dict[str, object]]:
    if not isinstance(config, dict):
        return []
    repos = config.get("repos")
    if not isinstance(repos, list):
        return []
    hooks: list[dict[str, object]] = []
    for repo in repos:
        if not isinstance(repo, dict) or repo.get("repo") != "local":
            continue
        value = repo.get("hooks")
        if isinstance(value, list):
            hooks.extend(hook for hook in value if isinstance(hook, dict))
    return hooks


def evaluate_gate_bindings(root: Path) -> Dimension:
    """Cross-check required scripts against executable commit-msg hook entries."""
    text = _read(root, ".pre-commit-config.yaml")
    try:
        hooks = _local_hooks(yaml.safe_load(text or ""))
    except yaml.YAMLError:
        hooks = []

    facts: list[Fact] = []
    for script_name in REQUIRED_GATE_SCRIPTS:
        script = root / "scripts" / script_name
        matching = [hook for hook in hooks if script_name in str(hook.get("entry", ""))]
        stage_ok = any("commit-msg" in (hook.get("stages") or []) for hook in matching)
        passed = script.is_file() and len(matching) == 1 and stage_ok
        facts.append(
            Fact(
                script_name,
                passed,
                f"script={script.is_file()} hook_count={len(matching)} commit-msg={stage_ok}",
            )
        )
    return Dimension("强制闸门绑定", tuple(facts))


def _expected_ruff_version(root: Path) -> str | None:
    """ruff 钉版的单一真源：conventions/_meta.yaml 的 toolchain.ruff"""
    text = _read(root, "conventions/_meta.yaml")
    if text is None:
        return None
    try:
        meta = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    toolchain = meta.get("toolchain") if isinstance(meta, dict) else None
    version = toolchain.get("ruff") if isinstance(toolchain, dict) else None
    return version if isinstance(version, str) and version else None


def evaluate_ci_projection(root: Path) -> Dimension:
    """Require the runnable workflow, template, and formatter pin to agree."""
    workflow = _read(root, ".github/workflows/ci.yml")
    template = _read(root, "docs/templates/devguard/.github/workflows/ci.yml")
    pre_commit = _read(root, ".pre-commit-config.yaml")
    template_matches = workflow is not None and workflow == template
    version = _expected_ruff_version(root)
    pins = set(re.findall(r"ruff==([0-9][0-9a-z.]*)", workflow or ""))
    formatter_matches = bool(
        version
        and workflow
        and pre_commit
        and pins == {version}
        and f"rev: v{version}" in pre_commit
        and "ruff format --check . --config src/coding/ruff.toml" in workflow
    )
    return Dimension(
        "CI模板投影",
        (
            Fact(
                "workflow-template text equality",
                template_matches,
                "CI 与权威模板文本一致"
                if template_matches
                else "CI 与 docs/templates/devguard 工作流发生漂移",
            ),
            Fact(
                "ruff formatter version parity",
                formatter_matches,
                f"CI 与 pre-commit 均按 toolchain 真源使用 ruff {version} 且 CI 执行 format --check"
                if formatter_matches
                else (
                    f"CI/pre-commit 的 ruff 钉版与 toolchain 真源（{version}）不一致或格式闸门缺失"
                ),
            ),
        ),
    )


def _default_runner(command: list[str]) -> tuple[int, str]:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode, output


def _executable_fact(
    root: Path,
    name: str,
    script_name: str,
    args: list[str],
    runner: CommandRunner,
) -> Dimension:
    script = root / "scripts" / script_name
    if not script.is_file():
        fact = Fact(name, False, f"缺 scripts/{script_name}")
    else:
        return_code, output = runner([sys.executable, str(script), *args])
        summary = output.splitlines()[-1] if output else f"exit={return_code}"
        fact = Fact(name, return_code == 0, summary)
    return Dimension(name, (fact,))


def evaluate_repository(
    root: Path,
    command_runner: CommandRunner | None = None,
) -> ConsistencyReport:
    root = root.resolve()
    runner = command_runner or _default_runner
    dimensions = (
        evaluate_progress_truth(root),
        evaluate_spec_contract(root),
        evaluate_gate_bindings(root),
        evaluate_ci_projection(root),
        _executable_fact(root, "元数据可复现", "render_meta.py", ["--check"], runner),
        _executable_fact(
            root,
            "故障注入拦截",
            "check_enforcement.py",
            ["--threshold", "90", "--repo-root", str(root)],
            runner,
        ),
    )
    return ConsistencyReport(dimensions)


def format_report(report: ConsistencyReport, threshold: float = DEFAULT_THRESHOLD) -> str:
    lines = ["=== 一致性事实矩阵 ==="]
    for dimension in report.dimensions:
        lines.append(f"{dimension.name}: {dimension.passed}/{dimension.total}")
        for fact in dimension.facts:
            state = "PASS" if fact.passed else "FAIL"
            lines.append(f"  [{state}] {fact.name}: {fact.detail}")
    lines.append(
        f"总计: {report.passed}/{report.total} = {report.score:.1f}% (阈值 {threshold:.1f}%)"
    )
    lines.append("OK 一致性达标" if report.score >= threshold else "FAIL 一致性未达标")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    report = evaluate_repository(args.repo_root)
    print(format_report(report, args.threshold))
    return 0 if report.score >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(main())
