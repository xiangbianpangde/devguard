# Scaffold payload

This directory is not copied recursively. `scripts/setup_scaffold.py` selects
every file through an explicit source-to-destination manifest.

- `core/` is the smallest runnable governance and CI closure.
- `optional/` only adds team ownership and durable decision/report folders.

Rendered `*.tmpl` files become root project documents. Cache, backup, temporary,
and editor-generated files are forbidden from this payload.

The installer composes rather than discards an existing ECC/global
`core.hooksPath`: external `pre-commit` and `pre-push` launchers are chained
with the generated project hooks, while a local `.git/hooks` path makes the
combined chain effective without mutating user-level Git configuration.
