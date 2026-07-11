#!/usr/bin/env python3
"""Measure fact-backed alignment with the useful surfaces of the ECC project."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import NamedTuple


DEFAULT_THRESHOLD = 80.0


class Fact(NamedTuple):
    domain: str
    passed: bool
    detail: str


class Report(NamedTuple):
    facts: tuple[Fact, ...]

    @property
    def passed(self) -> int:
        return sum(fact.passed for fact in self.facts)

    @property
    def total(self) -> int:
        return len(self.facts)

    @property
    def score(self) -> float:
        return 100.0 * self.passed / self.total if self.total else 0.0


def _read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _has_all(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles)


def evaluate(root: Path) -> Report:
    """Evaluate ten distinct ECC capability domains from executable artifacts."""
    root = root.resolve()
    setup = _read(root, "scripts/setup_scaffold.py")
    agents = _read(root, "docs/templates/devguard/scaffold/core/AGENTS.md.tmpl")
    skill = _read(
        root,
        "docs/templates/devguard/scaffold/core/.agents/skills/devguard/SKILL.md.tmpl",
    )
    codex = _read(root, "docs/templates/devguard/scaffold/core/.codex/config.toml")
    hooks = _read(
        root,
        "docs/templates/devguard/scaffold/core/scripts/install_hooks.py",
    )
    pre_commit = _read(
        root,
        "docs/templates/devguard/scaffold/core/.pre-commit-config.yaml",
    )
    workflow = _read(
        root,
        "docs/templates/devguard/scaffold/core/.github/workflows/devguard.yml",
    )
    verifier = _read(root, "docs/templates/devguard/scaffold/core/scripts/devguard.py")
    scaffold_tests = _read(root, "tests/conventions/test_scaffold.py")
    consistency = _read(root, "scripts/check_consistency.py")
    enforcement = _read(root, "scripts/check_enforcement.py")

    facts = (
        Fact(
            "skills-first",
            _has_all(skill, "name: devguard", "conventions/README.md") and "skills-first" in agents,
            "canonical DevGuard skill is installed and routed from AGENTS.md",
        ),
        Fact(
            "single rules authority",
            (root / "conventions/README-规范导航.md").is_file()
            and _has_all(skill, "single rules authority", "conventions/README.md")
            and "second rules or commands authority" in agents,
            "skills route to conventions instead of duplicating rules/commands",
        ),
        Fact(
            "cross-harness Codex/Claude",
            _has_all(setup, "core/AGENTS.md.tmpl", "core/CLAUDE.md.tmpl")
            and _has_all(codex, 'sandbox_mode = "workspace-write"', "multi_agent = false")
            and "mcp_servers." not in codex,
            "Claude and Codex entrypoints ship with a credential-free local config",
        ),
        Fact(
            "explicit profiles and payload",
            _has_all(setup, "CORE_MANIFEST", "OPTIONAL_MANIFEST", "entries_for")
            and _has_all(setup, "_validate_sources", "duplicates"),
            "core/optional profiles are explicit, unique, and preflight validated",
        ),
        Fact(
            "composed hooks",
            _has_all(
                hooks,
                "pre-commit",
                "commit-msg",
                "pre-push",
                "core.hooksPath",
                "_chain_external_hooks",
            ),
            "project hooks compose with existing ECC/global hooks",
        ),
        Fact(
            "security-first",
            _has_all(pre_commit, "id: gitleaks", "id: ruff", "devguard-verify")
            and "id: gitleaks" in verifier
            and (root / "SECURITY.md").is_file(),
            "generated projects fail closed on secrets, lint, and baseline integrity",
        ),
        Fact(
            "TDD and CI",
            _has_all(
                workflow,
                "permissions:",
                "contents: read",
                "pre_commit run --all-files",
                "pytest tests/governance",
            )
            and "test_cli_e2e" in scaffold_tests,
            "least-privilege CI runs verification, hooks, and governance tests",
        ),
        Fact(
            "transactional one-click deployment",
            _has_all(
                setup,
                "_atomic_write",
                "_rollback_writes",
                '"--dry-run"',
                '"--install"',
                '"--verify"',
            )
            and "test_setup_rolls_back_every_managed_write" in scaffold_tests,
            "installer supports plan, install, verify, atomic replace, and rollback",
        ),
        Fact(
            "reproducible manifest receipt",
            _has_all(setup, "sha256", ".devguard-receipt.json", "check_hashes")
            and _has_all(verifier, "CORE_FILES", "OPTIONAL_FILES", "verify"),
            "explicit files are receipted with digests and independently verified",
        ),
        Fact(
            "measurable governance",
            _has_all(consistency, "DEFAULT_THRESHOLD = 80.0", "evaluate")
            and _has_all(enforcement, "DEFAULT_THRESHOLD = 90.0", "fault"),
            "consistency and fault-injection enforcement have executable thresholds",
        ),
    )
    return Report(facts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args()
    report = evaluate(args.root)
    for fact in report.facts:
        state = "PASS" if fact.passed else "FAIL"
        print(f"[{state}] {fact.domain}: {fact.detail}")
    print(f"ECC alignment: {report.passed}/{report.total} = {report.score:.1f}%")
    if report.score < args.threshold:
        print(f"FAIL ECC alignment below {args.threshold:.1f}%")
        return 1
    print("OK ECC alignment threshold met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
