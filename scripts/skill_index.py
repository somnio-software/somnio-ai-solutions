"""Shared helpers to discover and parse the skills in this repository.

Stdlib only — no third-party dependencies, so every script here runs with the
system `python3` on any machine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PLUGIN_DIR = ROOT / "plugins" / "somnio-ai-solutions"
PLUGIN_SKILLS_DIR = PLUGIN_DIR / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_SKILL_LINES = 500


@dataclass
class Skill:
    """One skill folder under `skills/`."""

    name: str
    path: Path
    frontmatter: dict[str, str] = field(default_factory=dict)
    body: str = ""

    @property
    def skill_md(self) -> Path:
        return self.path / "SKILL.md"

    @property
    def description(self) -> str:
        return self.frontmatter.get("description", "").strip()

    @property
    def rel_path(self) -> str:
        return self.path.relative_to(ROOT).as_posix()

    @property
    def symlink(self) -> Path:
        return PLUGIN_SKILLS_DIR / self.path.name


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the YAML frontmatter of a SKILL.md.

    Deliberately minimal: top-level `key: value` pairs plus folded (`>`) and
    literal (`|`) block scalars. That is the whole surface a SKILL.md needs.
    Returns `(frontmatter, body)`; an empty dict means no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, text

    data: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
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
            joiner = "\n" if raw.startswith("|") else " "
            data[key] = joiner.join(part for part in block if part)
            continue
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            raw = raw[1:-1]
        data[key] = raw
        i += 1

    return data, "\n".join(lines[end + 1 :])


def load_skill(path: Path) -> Skill:
    skill = Skill(name=path.name, path=path)
    if skill.skill_md.is_file():
        frontmatter, body = parse_frontmatter(skill.skill_md.read_text(encoding="utf-8"))
        skill.frontmatter = frontmatter
        skill.body = body
        skill.name = frontmatter.get("name", path.name)
    return skill


def load_skills() -> list[Skill]:
    """Every skill folder under `skills/`, sorted by folder name."""
    if not SKILLS_DIR.is_dir():
        return []
    return [
        load_skill(entry)
        for entry in sorted(SKILLS_DIR.iterdir())
        if entry.is_dir() and not entry.name.startswith(".")
    ]


def first_sentence(text: str) -> str:
    """First sentence of a description, for the README table."""
    text = " ".join(text.split())
    match = re.search(r"(?<=[.!?])\s", text)
    return text[: match.start()] if match else text
