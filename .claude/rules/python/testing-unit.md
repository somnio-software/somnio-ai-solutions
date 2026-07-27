---
description: Unit testing with stdlib unittest — 100% per-file line coverage gate, descriptive test names, real temporary repositories over mocks, in-process main() calls, one behaviour per test. Applies to all files under tests/.
globs: tests/**/*.py
alwaysApply: false
---

## Best Practices

- **stdlib `unittest`, no pytest.** pytest, `pytest-mock` and Hypothesis are all
  third-party; the suite must run with a bare `python3`. Use `unittest.TestCase`
  and its assertions (`assertEqual`, `assertIn`, `assertTrue`), and run
  everything through `tests/run_tests.py`.

- **Line coverage is 100% per file, and it never goes down.** The gate is
  per-file, not an aggregate average: every script under `skills/*/scripts/` must
  be fully exercised. A script no test imports reports 0% and fails. When a line
  is genuinely unreachable, delete it — dead code is the usual cause.

- **Name tests `test_<unit>_<scenario>_<expected>`.**
  `test_missing_symlink_is_an_error` states the contract without reading the
  body; `test_validate_2` states nothing.

- **One behaviour per test.** A test that asserts five unrelated things reports
  only the first failure and hides the rest.

- **Real temporary directories, not mocks.** These scripts exist to manipulate
  the filesystem, so a mocked `Path` would test the mock. Build a throwaway
  repository (`FakeRepo`), act on it, assert on what is on disk, and let the
  context manager delete it. There is no mocking library available and none is
  needed.

- **Call `main()` in-process, never through a subprocess.** Patch `sys.argv`,
  capture stdout and stderr, assert on the returned exit code. A subprocess is
  invisible to the coverage tracer and turns a fast test into a slow one — this
  is why `run_main` exists in `tests/helpers.py`.

- **Assert inside the `with` block.** A `FakeRepo` is deleted on exit; reading
  `repo.readme` afterwards raises `FileNotFoundError` and disguises a passing
  test as a broken one.

- **Test the failure paths as hard as the happy path.** Wrong exit codes, missing
  files, malformed frontmatter and stale symlinks are what the scripts exist to
  catch; they are the tests that matter.

- **The repository is its own fixture.** Keep the tests that run the validator
  and the README sync against this repo itself — they catch drift no synthetic
  fixture would.

## Anti-Patterns

- **A third-party import in a test** — it breaks the zero-dependency guarantee
  the whole harness rests on.
- **Lowering the coverage threshold to make a push succeed** — add the test, or
  delete the unreachable code.
- **Asserting on a `FakeRepo` after the `with` block closes** — the directory is
  gone.
- **`subprocess.run([sys.executable, script])`** — untraceable by the coverage
  gate, and slow.
- **A test whose name does not say what broke** when it fails.
