---
description: Python error handling for skill scripts — solve don't defer, EAFP, narrowest except, never swallow silently, actionable messages, exit codes over exceptions at the CLI boundary. Applies to all .py files.
globs: **/*.py
alwaysApply: false
---

## Best Practices

- **Solve, don't defer.** A script exists to be more reliable than improvised
  code. When a condition is recoverable, handle it in the script — create the
  missing directory, replace the stale symlink, fall back to a documented default
  — instead of failing and leaving Claude to guess. Deferring to the model is the
  failure mode these scripts exist to prevent.

- **Fail loudly when it is not recoverable.** Print to `stderr` with the prefix
  `error:` and return a non-zero code. Silence, or a zero exit after a failed
  step, is worse than a crash: CI and the pre-push hook both trust the code.

- **Error messages must name the fix, not just the fault.** "missing plugin
  symlink `plugins/x/skills/y` — re-run with --fix" is actionable; "invalid
  configuration" is not. Include the offending value and the available
  alternatives whenever you have them.

- **EAFP over LBYL.** Attempt the operation and handle the exception rather than
  pre-checking a condition that can change between the check and the use. The
  exception is user-facing validation, where a check produces a far better
  message than a traceback.
  Source: https://realpython.com/ref/best-practices/exception-handling/

- **Catch the narrowest exception that covers the failure.** `except
  FileNotFoundError`, never `except Exception`, and never a bare `except:` —
  those swallow `KeyboardInterrupt` and every programming error along with the
  case you meant to handle. Source: https://peps.python.org/pep-0020/

- **Never swallow an exception silently.** An empty `except` or one that only
  passes is forbidden. If suppression is genuinely correct, use
  `contextlib.suppress(SpecificError)` and put the reason in a comment.

- **Exceptions do not cross the CLI boundary.** `main` converts failures into an
  exit code and a message; a traceback reaching the user is a defect, except when
  it is a genuine bug, where the traceback is the right output.

- **Validate inputs before doing destructive work.** Check the name, the target
  and the existing state first, then act. A script that half-creates a skill and
  then fails leaves the repository worse than it found it.

- **No control flow by exception.** Missing keys, empty lists and absent optional
  values are expected branches — use `if`/`else` and early returns.

## Anti-Patterns

- **`except Exception: pass`** — the error is now invisible and the state unknown.
- **Returning `0` after a step failed** — CI reports green on a broken repository.
- **A message with no context** ("failed", "invalid input") — the reader cannot
  act on it.
- **Letting a partial write stand after an error** — validate first, or clean up.
- **Raising on an expected condition** (no skills yet, no README markers) —
  report it and return the appropriate code.
