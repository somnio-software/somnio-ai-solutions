# Git hooks

Versioned git hooks for this repo. They live here (instead of `.git/hooks`, which
is not tracked) so everyone shares the same checks.

## Enable

Run once per clone:

```bash
git config core.hooksPath .githooks
```

Or `make hooks`, which runs exactly that.

## Hooks

### `pre-push`

Runs the same three gates as CI and blocks the push if any fails:

1. **Skill validation** — every skill under `skills/` against Anthropic's SKILL.md
   spec and Somnio's standard (`somnio-skill-verifier`).
2. **README index** — fails if the generated skills table no longer matches the
   skills on disk.
3. **Tests and coverage** — the harness suite, with **per-file** line coverage of
   every script under `skills/*/scripts/` at **100%** (enforced per file, not as an
   aggregate average). A script no test imports reports 0% and fails.

- Lower the threshold for one push: `COVERAGE_MIN=95 git push` (the committed
  default is 100 and is not meant to be reduced)
- Bypass intentionally (e.g. docs-only change): `git push --no-verify`

Coverage is measured with the stdlib `trace` module through `tests/run_tests.py`,
so the hook needs nothing but the system `python3` — the same zero-dependency
guarantee the skills themselves have.
