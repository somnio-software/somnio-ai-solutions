#!/usr/bin/env python3
"""Validate every skill in this repository.

Checks frontmatter, naming, size limits, and the plugin symlinks. Exits with a
non-zero status when an error is found so it can gate CI.

Usage:
    python3 scripts/validate-skills.py [--strict]

    --strict   treat warnings as errors
"""

from __future__ import annotations

import sys

from skill_index import (
    MAX_DESCRIPTION_LEN,
    MAX_NAME_LEN,
    MAX_SKILL_LINES,
    NAME_RE,
    PLUGIN_SKILLS_DIR,
    ROOT,
    SKILLS_DIR,
    Skill,
    load_skills,
)

TRIGGER_HINTS = ("use when", "use this skill when", "use it when")


def check_skill(skill: Skill) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    folder = skill.path.name

    if not skill.skill_md.is_file():
        return [f"missing {skill.rel_path}/SKILL.md"], warnings

    if not skill.frontmatter:
        errors.append("SKILL.md has no YAML frontmatter (must start with `---`)")
        return errors, warnings

    name = skill.frontmatter.get("name", "").strip()
    if not name:
        errors.append("frontmatter is missing `name`")
    else:
        if name != folder:
            errors.append(f"frontmatter `name: {name}` does not match folder `{folder}`")
        if not NAME_RE.match(name):
            errors.append(f"`name: {name}` is not kebab-case (a-z, 0-9 and single dashes)")
        if len(name) > MAX_NAME_LEN:
            errors.append(f"`name` is {len(name)} chars, max is {MAX_NAME_LEN}")

    description = skill.description
    if not description:
        errors.append("frontmatter is missing `description`")
    else:
        if len(description) > MAX_DESCRIPTION_LEN:
            errors.append(
                f"`description` is {len(description)} chars, max is {MAX_DESCRIPTION_LEN}"
            )
        if len(description) < 40:
            warnings.append("`description` is very short — Claude may never trigger the skill")
        if not any(hint in description.lower() for hint in TRIGGER_HINTS):
            warnings.append("`description` does not say when to use the skill (\"Use when ...\")")
        if "{{" in description:
            errors.append("`description` still contains template placeholders")

    line_count = len(skill.skill_md.read_text(encoding="utf-8").splitlines())
    if line_count > MAX_SKILL_LINES:
        warnings.append(
            f"SKILL.md is {line_count} lines (soft limit {MAX_SKILL_LINES}) — "
            "move detail into references/"
        )

    if not any(line.startswith("# ") for line in skill.body.splitlines()):
        warnings.append("SKILL.md body has no H1 title")

    link = skill.symlink
    if not link.is_symlink():
        errors.append(
            f"missing plugin symlink — run: ln -s ../../../skills/{folder} "
            f"plugins/somnio-ai-solutions/skills/{folder}"
        )
    elif link.resolve() != skill.path.resolve():
        errors.append(f"plugin symlink `{link.name}` points to {link.resolve()}")

    return errors, warnings


def check_repo(skills: list[Skill]) -> list[str]:
    errors: list[str] = []

    if not SKILLS_DIR.is_dir():
        return ["`skills/` directory is missing"]

    folders = {skill.path.name for skill in skills}
    if PLUGIN_SKILLS_DIR.is_dir():
        for entry in sorted(PLUGIN_SKILLS_DIR.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.name not in folders:
                errors.append(
                    f"orphan plugin symlink `plugins/somnio-ai-solutions/skills/{entry.name}` "
                    "has no matching skill"
                )
    else:
        errors.append("`plugins/somnio-ai-solutions/skills/` directory is missing")

    seen: dict[str, str] = {}
    for skill in skills:
        declared = skill.frontmatter.get("name", "").strip()
        if declared and declared in seen:
            errors.append(f"duplicate skill name `{declared}` in {seen[declared]} and {skill.rel_path}")
        elif declared:
            seen[declared] = skill.rel_path

    return errors


def main() -> int:
    strict = "--strict" in sys.argv[1:]
    skills = load_skills()

    print(f"Validating {len(skills)} skill(s) in {ROOT.name}/skills\n")

    total_errors = 0
    total_warnings = 0

    for error in check_repo(skills):
        print(f"  ✗ repo: {error}")
        total_errors += 1

    for skill in skills:
        errors, warnings = check_skill(skill)
        total_errors += len(errors)
        total_warnings += len(warnings)
        mark = "✗" if errors else ("!" if warnings else "✓")
        print(f"  {mark} {skill.path.name}")
        for error in errors:
            print(f"      error:   {error}")
        for warning in warnings:
            print(f"      warning: {warning}")

    print(f"\n{total_errors} error(s), {total_warnings} warning(s)")

    if total_errors or (strict and total_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
