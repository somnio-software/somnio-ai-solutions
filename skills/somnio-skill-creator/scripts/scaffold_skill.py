#!/usr/bin/env python3
"""Scaffold a new Claude Code skill and wire it into the repository's plugins.

Creates `skills/<name>/` from the bundled template, symlinks it into every
plugin found under `plugins/`, and refreshes the README skills table.
Stdlib only — runs with the system `python3` in any Somnio skills repository.

Usage:
    python3 scaffold_skill.py <skill-name> --description "What it does. Use when ..."
    python3 scaffold_skill.py <skill-name> --repo-root ../somnio-finance-ai

Exit codes: 0 = created, 1 = refused (invalid name or already exists), 2 = bad usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "skill-template"
SYNC_README = SCRIPT_DIR / "sync_readme.py"

# Same limits as Anthropic's SKILL.md spec — see references/authoring-standard.md.
MAX_NAME_LEN = 64
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("anthropic", "claude")

DEFAULT_DESCRIPTION = (
    "States what this skill produces and for whom. "
    "Use this skill when the user asks to <trigger>, or mentions <keyword>."
)


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def validate_name(name: str) -> str | None:
    if not NAME_RE.match(name):
        return f"'{name}' must be kebab-case: lowercase letters, numbers and single hyphens"
    if len(name) > MAX_NAME_LEN:
        return f"'{name}' is {len(name)} chars, the spec allows {MAX_NAME_LEN}"
    for word in RESERVED_WORDS:
        if word in name:
            return f"'{name}' contains the reserved word '{word}', which the spec forbids"
    return None


def title_from(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def find_plugins(repo_root: Path) -> list[Path]:
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        return []
    return sorted(
        p for p in plugins_dir.iterdir() if p.is_dir() and (p / ".claude-plugin" / "plugin.json").is_file()
    )


def render_template(target: Path, name: str, description: str) -> None:
    for path in sorted(target.rglob("*")):
        if path.name == ".gitkeep":
            path.unlink()
            continue
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in (
            ("{{SKILL_NAME}}", name),
            ("{{SKILL_TITLE}}", title_from(name)),
            ("{{SKILL_DESCRIPTION}}", description),
        ):
            text = text.replace(key, value)
        path.write_text(text, encoding="utf-8")


def link_into_plugins(repo_root: Path, name: str, plugins: list[Path]) -> list[str]:
    created: list[str] = []
    for plugin in plugins:
        links_dir = plugin / "skills"
        links_dir.mkdir(parents=True, exist_ok=True)
        link = links_dir / name
        if link.is_symlink() or link.exists():
            link.unlink()
        depth = len(links_dir.relative_to(repo_root).parts)
        link.symlink_to(Path(*[".."] * depth) / "skills" / name)
        created.append(str(link.relative_to(repo_root)))
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="skill name in kebab-case, matching its folder")
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION, help="frontmatter description")
    parser.add_argument("--repo-root", default=".", help="repository root (default: current directory)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        return fail(f"{repo_root} is not a directory")

    problem = validate_name(args.name)
    if problem:
        return fail(problem)

    if not TEMPLATE_DIR.is_dir():
        return fail(f"template not found at {TEMPLATE_DIR}")

    skill_dir = repo_root / "skills" / args.name
    if skill_dir.exists():
        return fail(f"{skill_dir.relative_to(repo_root)} already exists")

    skill_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-R", str(TEMPLATE_DIR), str(skill_dir)], check=True)
    render_template(skill_dir, args.name, args.description)

    plugins = find_plugins(repo_root)
    links = link_into_plugins(repo_root, args.name, plugins)
    if not plugins:
        print("warning: no plugin found under plugins/ — no symlink was created", file=sys.stderr)

    readme_synced = False
    if SYNC_README.is_file():
        result = subprocess.run(
            [sys.executable, str(SYNC_README), "--repo-root", str(repo_root)],
            capture_output=True,
            text=True,
        )
        readme_synced = result.returncode == 0

    print(f"Created skills/{args.name}")
    print(f"  skills/{args.name}/SKILL.md            write the description first")
    print(f"  skills/{args.name}/scripts/            deterministic helpers (delete if unused)")
    print(f"  skills/{args.name}/references/         long-form material (delete if unused)")
    for link in links:
        print(f"  {link}   symlink to skills/{args.name}")
    if readme_synced:
        print("  README.md                             skills table regenerated")
    print()
    print("Next: fill in SKILL.md, remove the authoring notes, then validate with")
    print("      python3 skills/somnio-skill-verifier/scripts/validate_skills.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
