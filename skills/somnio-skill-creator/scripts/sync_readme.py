#!/usr/bin/env python3
"""Regenerate the README skills table from each SKILL.md frontmatter.

The table is written between the `<!-- skills:start -->` and `<!-- skills:end -->`
markers, so the README index never drifts from the skills on disk.
Stdlib only — runs with the system `python3` in any Somnio skills repository.

Usage:
    python3 sync_readme.py [--repo-root .] [--check]

    --check   do not write; exit 1 if the table is out of date

Exit codes: 0 = in sync (or updated), 1 = out of date with --check, or no markers.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START = "<!-- skills:start -->"
END = "<!-- skills:end -->"
EMPTY_TABLE = "_No skills yet._"


def parse_frontmatter(text: str) -> dict[str, str]:
    """Top-level `key: value` pairs plus folded/literal block scalars."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}

    data: dict[str, str] = {}
    i = 1
    while i < end:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        if not match:
            i += 1
            continue
        key, raw = match.group(1), match.group(2).strip()
        if raw in (">", "|", ">-", "|-", ">+", "|+"):
            block: list[str] = []
            i += 1
            while i < end and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                block.append(lines[i].strip())
                i += 1
            data[key] = ("\n" if raw.startswith("|") else " ").join(p for p in block if p)
            continue
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            raw = raw[1:-1]
        data[key] = raw
        i += 1
    return data


def first_sentence(text: str) -> str:
    """The 'what it does' half of a description, for the README table."""
    text = " ".join(text.split())
    match = re.search(r"(?<=[.!?])\s", text)
    return text[: match.start()] if match else text


def build_table(repo_root: Path) -> str:
    skills_dir = repo_root / "skills"
    folders = (
        sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
        if skills_dir.is_dir()
        else []
    )
    if not folders:
        return f"{EMPTY_TABLE} Ask Claude for the `somnio-skill-creator` skill to add the first one."

    rows = ["| Skill | Description |", "|:------|:------------|"]
    for folder in folders:
        skill_md = folder / "SKILL.md"
        description = ""
        if skill_md.is_file():
            description = parse_frontmatter(skill_md.read_text(encoding="utf-8")).get("description", "")
        summary = first_sentence(description.strip()) or "_No description._"
        rows.append(f"| [`{folder.name}`](./skills/{folder.name}) | {summary} |")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo-root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--check", action="store_true", help="fail instead of writing when out of date")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    readme = repo_root / "README.md"
    if not readme.is_file():
        print(f"error: {readme} not found", file=sys.stderr)
        return 1

    content = readme.read_text(encoding="utf-8")
    if START not in content or END not in content:
        print(f"error: README.md is missing the {START} / {END} markers", file=sys.stderr)
        return 1

    head, rest = content.split(START, 1)
    _, tail = rest.split(END, 1)
    updated = f"{head}{START}\n\n{build_table(repo_root)}\n\n{END}{tail}"

    if updated == content:
        print("README.md skills table is up to date")
        return 0
    if args.check:
        print("README.md skills table is out of date — run sync_readme.py", file=sys.stderr)
        return 1

    readme.write_text(updated, encoding="utf-8")
    print("README.md skills table updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
