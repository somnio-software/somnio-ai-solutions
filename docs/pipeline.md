# Pipeline

[`.github/workflows/skills.yml`](../.github/workflows/skills.yml) owns everything
mechanical.

| Trigger | What runs |
|:--------|:----------|
| Pull request touching `skills/`, `plugins/` or `tests/` | Validates every skill, fails if the README table is stale, runs the tests with the coverage gate |
| Push to `main` touching the same paths | Repairs symlinks, syncs the README, rebuilds `plugins/somnio-ai-solutions.zip`, verifies it is self-contained, and commits it back |

## Validation job

The same three commands as `make check` and as the [pre-push hook](testing.md):
`validate_skills.py`, `sync_readme.py --check`, and `run_tests.py --min 100`. It
runs on every pull request, so nothing merges past a broken skill or an untested
line.

## Packaging job

Runs only on `main`, and only after validation passes. It:

1. repairs plugin symlinks and syncs the README, so a merge cannot leave the
   plugin half-wired;
2. rebuilds the archive with the `zip` command documented in
   [`CLAUDE.md`](../CLAUDE.md);
3. verifies every skill's `SKILL.md` is actually inside the archive — `zip`
   dereferences symlinks, and this proves it did;
4. commits the result with `[skip ci]`.

**Never commit a locally built `.zip`.** The pipeline owns that file.

Timestamps are normalized before zipping, so an unrelated push produces a
byte-identical archive and therefore no commit at all.

## Coverage threshold

The workflow pins `COVERAGE_MIN: "100"`. It is the same number as the hook
default and the `Makefile` default, and it is not meant to be lowered — see
[Testing](testing.md).
