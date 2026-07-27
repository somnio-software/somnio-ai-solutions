---
description: Python function design — single responsibility, early returns, pure functions, isolated side effects, dataclasses over ad-hoc dicts, keyword-only flags. Applies to all .py files.
globs: **/*.py
alwaysApply: false
---

## Best Practices

- **Single responsibility.** A function does one thing at one level of
  abstraction, so it can be understood, tested and replaced in isolation. When
  the name needs an "and", split it.

- **Early returns over nesting.** Handle the guard cases first and return; keep
  the main path at the lowest indentation level. Three levels of nesting in a
  script this small means a helper is missing.

- **Pure functions wherever the work is a transformation.** A function that takes
  values and returns values needs no fixtures, no temporary directory and no
  mocks to test. `first_sentence(text)` and `executable_lines(path)` are the
  shape to aim for.

- **Isolate the side effects.** Reading, writing, symlinking and printing belong
  in a small number of clearly named functions; the logic that decides *what* to
  write stays pure. This is why the validator computes findings first and prints
  them afterwards.

- **Return data, do not print it, from anything that is not `main`.** Collect
  findings, results or paths and let the caller decide how to render them —
  otherwise the function is untestable and unreusable.

- **Dataclasses instead of dicts and tuples** for anything with a fixed shape.
  `Finding(level, message)` documents itself and fails loudly on a typo, where
  `{"lvl": ...}` fails silently three functions later.

- **Keyword-only arguments for flags.** `check_plugin_wiring(skill, plugins, fix=True)`
  cannot be misread; `check_plugin_wiring(skill, plugins, True)` can. Any boolean
  parameter is a candidate for `*`-enforced keyword-only.

- **Default arguments are immutable.** Use `None` and build the container inside,
  or `field(default_factory=list)` in a dataclass. A shared mutable default is a
  bug that survives every review.
  Source: https://docs.python.org/3/tutorial/controlflow.html#default-argument-values

## Anti-Patterns

- **A function that both computes and prints** — it can only be tested by
  capturing stdout, and it can never be reused.
- **Boolean parameters passed positionally** — the call site says nothing about
  what `True` means.
- **A dict passed between five functions**, each knowing a different subset of
  its keys — make it a dataclass.
- **Mutable default arguments** (`def f(items=[])`) — the list is shared across
  every call.
- **Deep nesting to avoid an early return** — invert the condition and return.
