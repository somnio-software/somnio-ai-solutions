---
description: Python code style — PEP 8 naming, 110-column lines, absolute stdlib-only imports in three groups, docstrings where the signature is not self-explanatory. Applies to all .py files.
globs: **/*.py
alwaysApply: false
---

## Best Practices

- **PEP 8 naming, without exception.** Modules and files: `snake_case`
  (`validate_skills.py`). Functions, variables, parameters: `snake_case`.
  Classes: `PascalCase`. Module-level immutable constants: `SCREAMING_SNAKE_CASE`
  (`MAX_NAME_LEN`). Never use `SCREAMING_SNAKE_CASE` for a mutable object.
  Source: https://peps.python.org/pep-0008/#naming-conventions

- **Line length is 110 columns.** Upstream uses Ruff's 88 default; this repo
  adopts 110 because these scripts print user-facing messages that read worse
  when wrapped. The limit is enforced by `tests/test_code_style.py`, not by a
  formatter. Source: https://peps.python.org/pep-0008/

- **No linter, no formatter, no dependency.** Ruff, Black and isort are all
  third-party, and every script here must run with a bare system `python3`.
  Style is therefore enforced by review plus the automated style test. Write the
  code the way the formatter would: the absence of a tool is not permission to
  drift.

- **Imports are absolute, stdlib only, and grouped.** Standard library first,
  then first-party (test helpers), separated by one blank line and sorted
  alphabetically inside each group. A third-party import is a defect in this
  repository, not a style issue. Source: https://peps.python.org/pep-0008/#imports

- **`from __future__ import annotations` at the top of every module**, before any
  other import. It keeps modern annotation syntax working on older interpreters
  the scripts may land on. Source: https://peps.python.org/pep-0563/

- **Every module opens with a docstring** stating what the file is for, and every
  script's docstring includes its `Usage:` block and exit codes — it is what
  `--help` and the reader both rely on. Source: https://peps.python.org/pep-0257/

- **Functions need a docstring when the name and signature do not already state
  the contract.** `check_name(skill) -> None` does not; `parse_frontmatter(text)`
  does, because the return shape and the supported YAML subset are not obvious.
  Prefer making the signature self-explanatory over writing a docstring that
  restates it. Source: https://peps.python.org/pep-0257/

- **Docstring summaries are one imperative line** ("Parse the frontmatter", not
  "Parses the frontmatter" or "This function parses..."), followed by a blank
  line and the details when there are any.
  Source: https://google.github.io/styleguide/pyguide.html

- **Comments explain why, never what.** A comment restating the code is noise; a
  comment justifying a constant, a workaround, or a non-obvious ordering is the
  most valuable line in the file.

## Anti-Patterns

- **A third-party import anywhere under `skills/` or `tests/`** — it breaks the
  zero-dependency guarantee that lets skills run in any environment.
- **Manual line breaks that fight readability** to satisfy the column limit —
  extract a variable or a helper instead.
- **A docstring that repeats the signature** ("Returns the name of the skill" on
  `skill_name() -> str`) — delete it.
- **Bare `# noqa`** — there is no linter to silence; if you are writing one, you
  are copying a habit from another project.
- **Mutable module-level state in `SCREAMING_SNAKE_CASE`** — the casing promises
  an invariant the object does not keep.
