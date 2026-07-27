---
description: Python type hints everywhere — annotate every signature, modern built-in generics and X | None unions, dataclass field annotations, no Any without a reason. Applies to all .py files.
globs: **/*.py
alwaysApply: false
---

## Best Practices

- **Annotate every function signature** — all parameters and the return type,
  including `-> None`. In a repository with no type checker, the annotation is
  the contract: it is what the next reader and Claude both work from.
  Source: https://peps.python.org/pep-0484/

- **Use modern built-in generics** (PEP 585): `list[str]`, `dict[str, set[int]]`,
  `tuple[dict[str, str], str]`. Never `List`, `Dict` or `Tuple` from `typing`.
  Source: https://peps.python.org/pep-0585/

- **Use `X | Y` unions and `X | None`** (PEP 604) rather than `Union[...]` or
  `Optional[...]`. `from __future__ import annotations` makes both work on older
  interpreters. Source: https://peps.python.org/pep-0604/

- **Annotate dataclass fields and module-level constants** whose type is not
  obvious from the literal. `TARGETS: list[Path]` earns its annotation;
  `MAX_NAME_LEN = 64` does not.
  Source: https://peps.python.org/pep-0526/

- **Annotate collections built incrementally.** `findings: list[Finding] = []`
  states the intent that the empty literal cannot.

- **`Path`, not `str`, for filesystem paths.** Convert at the boundary — argparse
  gives strings, everything past that layer is a `Path`. A function taking
  `path: str` will eventually be called with a `Path` and break on
  concatenation.

- **No type checker, on purpose.** pyright, mypy and `ty` are all third-party;
  this repository takes no dependency. Annotations are reviewed by humans, so
  they must be correct *and* honest — a wrong annotation is worse than none.

- **`Any` needs a comment justifying it.** In practice nothing here needs it: if
  a signature reaches for `Any`, the design is usually wrong.

## Anti-Patterns

- **An unannotated function** — the reader has to run the code to learn what it
  takes.
- **`typing.List` / `typing.Optional`** — legacy spelling, gone from modern
  Python style.
- **`str` where a `Path` is meant** — string paths break the moment someone joins
  them with `/`.
- **An annotation that lies** (`-> str` on a function that can return `None`) —
  it actively misleads, since nothing checks it.
- **`Any` as a shortcut around a union** — write the union.
