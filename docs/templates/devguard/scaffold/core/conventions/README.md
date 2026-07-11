# Development conventions

The enforceable baseline is intentionally small:

- `.pre-commit-config.yaml` defines local pre-commit and commit-msg gates.
- `.github/workflows/devguard.yml` repeats the gates on the server.
- `scripts/devguard.py` verifies dependency and configuration closure.
- `tests/governance/` proves the verifier's minimum contract.

Project-specific architecture, API, testing, and deployment rules belong in
separate documents here. Every red line must name its automated check or be
explicitly classified as a human review item.
