# Agent rules

Python rules for this repository, adapted from
[`somnio-ai-tools/agent-rules/rules/python`](https://github.com/somnio-software/somnio-ai-tools/tree/main/agent-rules/rules/python).
They are loaded into every session through `@imports` in [`CLAUDE.md`](../../CLAUDE.md).

## What this repository's Python actually is

Every rule here is scoped to what this repo contains: small command-line scripts
bundled inside skills (`skills/*/scripts/*.py`) and their `unittest` suite. There
is no application, no package to publish, no framework, and — deliberately — **no
third-party dependency**, because a skill must run with the system `python3` on
any machine, including the sandboxed environments Claude executes them in.

That constraint is why the upstream rules were adapted rather than copied.

## Included

| Rule | Adaptation |
|:-----|:-----------|
| [`code-style.md`](python/code-style.md) | PEP 8 kept; Ruff replaced by review plus the automated style test, since Ruff is a dependency this repo cannot take. Line length 110. |
| [`module-structure.md`](python/module-structure.md) | `src/` layout, packaging and structlog dropped; replaced by the script-as-CLI contract that makes scripts importable and testable. |
| [`function-design.md`](python/function-design.md) | Kept nearly whole — it is stack-independent. |
| [`error-handling.md`](python/error-handling.md) | Layered exception translation replaced by the "solve, don't defer" rule and CLI exit codes. |
| [`typing.md`](python/typing.md) | Kept; pyright and `py.typed` dropped (dependency, and nothing is distributed as a package). |
| [`testing-unit.md`](python/testing-unit.md) | pytest, `pytest-mock` and Hypothesis replaced by stdlib `unittest` and real temporary repositories. |

## Excluded

- **`data-validation.md`** — Pydantic. No dependency, no schema layer here.
- **`testing-integration.md`** — testcontainers and external systems. The suite
  touches nothing but temporary directories.

If this repository ever grows an application, pull those two in from upstream
rather than reinventing them.
