# Contributing

1. Create a short-lived branch.
2. Add a failing test or specification for behavior changes.
3. Run `python scripts/devguard.py verify` and focused tests.
4. Use a Conventional Commit message such as `fix(api): reject invalid ids`.
5. Open a pull request and wait for the required DevGuard CI check.

Do not bypass a gate silently. Document any approved exception in the pull
request with owner, reason, scope, and expiry.
