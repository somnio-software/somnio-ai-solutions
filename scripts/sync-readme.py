#!/usr/bin/env python3
"""Regenerate the Skills table in README.md from each SKILL.md frontmatter.

The table lives between the `<!-- skills:start -->` and `<!-- skills:end -->`
markers, so the README is never hand-edited for a new skill.

Usage:
    python3 scripts/sync-readme.py [--check]

    --check   do not write; exit 1 if the README is out of date
"""

from __future__ import annotations

import sys

from skill_index import ROOT, first_sentence, load_skills

README = ROOT / "README.md"
START = "<!-- skills:start -->"
END = "<!-- skills:end -->"


def build_table() -> str:
    skills = load_skills()
    if not skills:
        return (
            "_No skills yet._ Create the first one with `make new-skill NAME=<skill-name>`."
        )

    rows = ["| Skill | Description |", "|:------|:------------|"]
    for skill in skills:
        folder = skill.path.name
        description = first_sentence(skill.description) or "_No description._"
        rows.append(f"| [`{folder}`](./{skill.rel_path}) | {description} |")
    return "\n".join(rows)


def main() -> int:
    check = "--check" in sys.argv[1:]

    if not README.is_file():
        print("README.md not found", file=sys.stderr)
        return 1

    content = README.read_text(encoding="utf-8")
    if START not in content or END not in content:
        print(f"README.md is missing the {START} / {END} markers", file=sys.stderr)
        return 1

    head, rest = content.split(START, 1)
    _, tail = rest.split(END, 1)
    updated = f"{head}{START}\n\n{build_table()}\n\n{END}{tail}"

    if updated == content:
        print("README.md skills table is up to date")
        return 0

    if check:
        print("README.md skills table is out of date — run `make sync`", file=sys.stderr)
        return 1

    README.write_text(updated, encoding="utf-8")
    print("README.md skills table updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
