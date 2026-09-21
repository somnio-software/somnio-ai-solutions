---
description: Python module structure for skill scripts — one script one job, importable with no import-time side effects, argparse CLI, main() returning an exit code, no packaging layer. Applies to all .py files.
globs: **/*.py
alwaysApply: false
---

## Best Practices

- **A script belongs to the skill that uses it.** Scripts live in
  `skills/<skill-name>/scripts/`, never in a shared top-level directory. A skill
  must stay self-contained: it is symlinked into plugins and zipped for upload,
  and anything outside its folder will not travel with it. Duplicating thirty
  lines of parsing between two skills is the correct trade against coupling them.

- **One script, one job, one CLI.** Each file exposes a single command with its
  own `argparse` parser, and its module docstring documents usage and exit codes.
  If a script grows a second unrelated mode, split it.

- **No side effects at import time.** Module level holds imports, constants,
  dataclasses and function definitions — nothing that touches the filesystem,
  parses `sys.argv`, or prints. This is what lets the test suite import a script
  and call it in-process instead of shelling out. Source: https://peps.python.org/pep-0008/

- **`main() -> int` plus `if __name__ == "__main__": sys.exit(main())`.** `main`
  reads `sys.argv` through `argparse` and returns the exit code; it never calls
  `sys.exit` directly, so tests can assert on the returned value.

- **Exit codes are part of the contract**, because CI and the pre-push hook
  branch on them: `0` success, `1` the work failed or found problems, `2` the
  invocation itself was wrong. Document them in the module docstring.

- **Paths come from the caller, not from the current working directory.** Every
  script accepts `--repo-root` and resolves its own location with
  `Path(__file__).resolve().parent`. That is what makes one script usable across
  all four `somnio-*-ai` repositories.

- **Absolute imports only, and no circular imports.** If two modules need each
  other, the shared concept belongs in a third one — but in this repository the
  correct answer is usually that the script is doing two jobs.

- **No packaging layer.** No `pyproject.toml`, no `setup.py`, no `src/` layout,
  no `__init__.py`. Nothing here is installed or distributed; scripts are run by
  path, by Claude or by CI.

## Anti-Patterns

- **A shared `lib/` at the repository root** — it does not survive being zipped
  into a plugin, so the skill silently breaks once installed.
- **Reading `sys.argv` or the filesystem at module scope** — the module can no
  longer be imported by a test.
- **`sys.exit()` from inside a helper** — it kills the test process; return a
  code or raise instead.
- **Assuming the current working directory is the repository root** — it is the
  user's shell, and it is often not.
- **`print()` as the only error channel** — errors go to `stderr`, results go to
  `stdout`.
