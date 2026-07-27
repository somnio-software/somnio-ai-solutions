# Testing

Every script inside a skill is covered by [`tests/`](../tests), and the gate is
**100% line coverage per file** — not an aggregate average. A script no test
imports reports 0% and fails.

```bash
make test        # run the suite (fast, no gate)
make coverage    # run it with the per-file 100% gate
make check       # validate + README sync + coverage, what CI runs
```

## How it works

The suite is stdlib `unittest`, driven by
[`tests/run_tests.py`](../tests/run_tests.py), which measures coverage with the
stdlib `trace` module — the same zero-dependency guarantee the skills have. There
is no pytest, no coverage package, and no mocking library.

Tests build real temporary repositories (`FakeRepo`) and call each script's
`main()` in-process through `run_main`, so exit codes, symlinks and generated
files are asserted against what actually lands on disk. A subprocess would be
invisible to the tracer, so it is never used.

Only the `if __name__ == "__main__":` guard is excluded from the gate.

| File | What it covers |
|:-----|:---------------|
| [`test_validate_skills.py`](../tests/test_validate_skills.py) | Frontmatter parsing, every check, plugin wiring, orphans, exit codes |
| [`test_scaffold_skill.py`](../tests/test_scaffold_skill.py) | Scaffolding, symlink depth, README sync, refusals |
| [`test_sync_readme.py`](../tests/test_sync_readme.py) | Table generation, idempotence, `--check` |
| [`test_code_style.py`](../tests/test_code_style.py) | The missing linter: line limit, docstrings, CLI contract, no third-party imports |
| [`test_docs.py`](../tests/test_docs.py) | Every relative link in the README and in `docs/` resolves, and the docs index is complete |

Two tests run against this repository itself rather than a fixture: the validator
must be clean and the README table in sync. They catch drift no synthetic
fixture would.

## The threshold does not move

When a line is hard to reach, either test it or delete it — dead code is the
usual cause. Lowering the threshold to get a change through is explicitly
forbidden by [the rules](../.claude/rules/python/testing-unit.md).

## Pre-push hook

Versioned in [`.githooks/`](../.githooks). Enable once per clone:

```bash
make hooks       # git config core.hooksPath .githooks
```

`pre-push` runs the same three gates as CI — skill validation, README sync, and
the tests at 100% per-file coverage — and blocks the push when any fails.

- Lower the threshold for one push: `COVERAGE_MIN=95 git push`
- Bypass intentionally, e.g. a docs-only change: `git push --no-verify`
