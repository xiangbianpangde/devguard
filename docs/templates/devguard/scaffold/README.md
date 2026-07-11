# Scaffold payload

This directory is not copied recursively. `scripts/setup_scaffold.py` selects
every file through an explicit source-to-destination manifest.

- `core/` is the smallest runnable governance and CI closure.
- `optional/` only adds team ownership and durable decision/report folders.

The core profile is cross-harness and skills-first: it installs `AGENTS.md`,
`CLAUDE.md`, a canonical `.agents/skills/devguard/` skill, and a credential-free
project-local `.codex/config.toml`. Rules remain authoritative in
`conventions/README.md`; no duplicate command catalog is generated.

Rendered `*.tmpl` files become root project documents. Cache, backup, temporary,
and editor-generated files are forbidden from this payload.

The installer composes rather than discards an existing ECC/global
`core.hooksPath`: external `pre-commit` and `pre-push` launchers are chained
with the generated project hooks, while a local `.git/hooks` path makes the
combined chain effective without mutating user-level Git configuration.

Use `--dry-run` to validate and list the complete payload without creating the
target. Managed writes use atomic replacement and transaction rollback, including
when `--force` is explicitly used for a non-empty directory.
