#!/usr/bin/env python3
"""Validate Claude Code skills against Anthropic's spec and Somnio's conventions.

Stdlib only — runs with the system `python3` in any Somnio skills repository.

Usage:
    python3 validate_skills.py                     # every skill under ./skills
    python3 validate_skills.py skills/my-skill     # one skill
    python3 validate_skills.py --repo-root ../other-repo
    python3 validate_skills.py --strict            # warnings are failures
    python3 validate_skills.py --fix               # repair plugin symlinks

Exit codes: 0 = clean, 1 = errors found (or warnings with --strict), 2 = bad usage.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Limits come from Anthropic's SKILL.md spec.
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
# Soft limit: SKILL.md is fully loaded into context once the skill triggers.
MAX_BODY_LINES = 500
# Below this a description almost never carries enough trigger terms.
MIN_DESCRIPTION_LEN = 40

# Spanish function words that do not occur in English prose. Trigger terms are
# quoted in a description, and quoted spans never reach this list.
SPANISH_MARKERS = frozenset(
    {
        "que", "para", "con", "del", "los", "las", "una", "por", "como", "cuando",
        "este", "esta", "pero", "también", "desde", "hasta", "sobre", "entre",
        "cada", "debe", "puede", "usuario", "archivo", "siguiente", "cualquier",
        "según", "además", "aunque", "mismo", "tiene",
    }
)
# Five distinct markers in stripped prose is unreachable by accident in English.
MIN_SPANISH_MARKERS = 5

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("anthropic", "claude")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
QUOTED_RE = re.compile(r"[\"“«][^\"”»]*[\"”»]")
WORD_RE = re.compile(r"[a-záéíóúñü]+")
# A file named for a language — labels/es.md, questions-es/…— is a translation.
LANGUAGE_NAME_RE = re.compile(r"(^|[-_.])[a-z]{2}$")
XML_TAG_RE = re.compile(r"<[a-zA-Z/][^>]*>")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FIRST_PERSON_RE = re.compile(r"\b(I|I'll|I can|we|we'll|you can|you should)\b", re.IGNORECASE)
TRIGGER_HINTS = ("use when", "use this skill when", "use it when", "usar cuando")
PLACEHOLDERS = ("{{", "<trigger", "<One-line summary", "TODO:", "FIXME")

ERROR = "error"
WARNING = "warning"


@dataclass
class Finding:
    level: str
    message: str


@dataclass
class Skill:
    path: Path
    frontmatter: dict[str, str] = field(default_factory=dict)
    body: str = ""
    findings: list[Finding] = field(default_factory=list)

    @property
    def folder(self) -> str:
        return self.path.name

    @property
    def skill_md(self) -> Path:
        return self.path / "SKILL.md"

    @property
    def description(self) -> str:
        return self.frontmatter.get("description", "").strip()

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == WARNING]

    def error(self, message: str) -> None:
        self.findings.append(Finding(ERROR, message))

    def warn(self, message: str) -> None:
        self.findings.append(Finding(WARNING, message))


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse SKILL.md YAML frontmatter.

    Deliberately minimal: top-level `key: value` pairs plus folded (`>`) and
    literal (`|`) block scalars, which is the whole surface a SKILL.md needs.
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

    return data, "\n".join(lines[end + 1 :])


def load_skill(path: Path) -> Skill:
    skill = Skill(path=path)
    if not skill.skill_md.is_file():
        skill.error(f"missing {skill.folder}/SKILL.md")
        return skill
    text = skill.skill_md.read_text(encoding="utf-8")
    skill.frontmatter, skill.body = parse_frontmatter(text)
    return skill


def discover_skills(repo_root: Path, targets: list[str]) -> list[Skill]:
    if targets:
        paths = [Path(t).resolve() for t in targets]
    else:
        skills_dir = repo_root / "skills"
        if not skills_dir.is_dir():
            return []
        paths = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    return [load_skill(p) for p in paths]


def find_plugins(repo_root: Path) -> list[Path]:
    """Find the plugin directories, i.e. folders holding a `.claude-plugin/plugin.json`."""
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        return []
    return sorted(
        p for p in plugins_dir.iterdir() if p.is_dir() and (p / ".claude-plugin" / "plugin.json").is_file()
    )


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #


def check_name(skill: Skill) -> None:
    name = skill.frontmatter.get("name", "").strip()
    if not name:
        skill.error("frontmatter is missing `name`")
        return
    if name != skill.folder:
        skill.error(f"frontmatter `name: {name}` does not match folder `{skill.folder}`")
    if not NAME_RE.match(name):
        skill.error(f"`name: {name}` must be lowercase letters, numbers and single hyphens")
    if len(name) > MAX_NAME_LEN:
        skill.error(f"`name` is {len(name)} chars, the spec allows {MAX_NAME_LEN}")
    for word in RESERVED_WORDS:
        if word in name.lower():
            skill.error(f"`name` cannot contain the reserved word '{word}'")
    if name in ("helper", "utils", "tools", "docs", "data", "files"):
        skill.warn(f"`name: {name}` is too generic to be recognisable among many skills")


def check_description(skill: Skill) -> None:
    description = skill.description
    if not description:
        skill.error("frontmatter is missing `description` — the skill will never trigger")
        return
    if len(description) > MAX_DESCRIPTION_LEN:
        skill.error(f"`description` is {len(description)} chars, the spec allows {MAX_DESCRIPTION_LEN}")
    if XML_TAG_RE.search(description):
        skill.error("`description` cannot contain XML tags")
    if any(token in description for token in PLACEHOLDERS):
        skill.error("`description` still contains template placeholders")
    if len(description) < MIN_DESCRIPTION_LEN:
        skill.warn("`description` is very short — add what it does and when to use it")
    if not any(hint in description.lower() for hint in TRIGGER_HINTS):
        skill.warn('`description` never says when to use the skill (start a sentence with "Use when ...")')
    match = FIRST_PERSON_RE.search(description)
    if match:
        skill.warn(f"`description` is not third person (found '{match.group(0)}') — write 'Creates ...'")


def check_body(skill: Skill) -> None:
    if not skill.frontmatter:
        skill.error("SKILL.md has no YAML frontmatter (the file must start with `---`)")
        return

    lines = skill.body.splitlines()
    if len(lines) > MAX_BODY_LINES:
        skill.warn(
            f"SKILL.md body is {len(lines)} lines (soft limit {MAX_BODY_LINES}) — "
            "move detail into references/ and link to it"
        )
    if not any(line.startswith("# ") for line in lines):
        skill.warn("SKILL.md body has no H1 title")
    if any(token in skill.body for token in PLACEHOLDERS):
        skill.error("SKILL.md still contains template placeholders or authoring notes")
    if "<!--" in skill.body and "delete this comment" in skill.body:
        skill.error("the authoring notes comment was not removed from SKILL.md")


def prose_only(text: str) -> str:
    """Strip code blocks, inline code and quoted spans, leaving the prose."""
    for pattern in (CODE_BLOCK_RE, INLINE_CODE_RE, QUOTED_RE):
        text = pattern.sub(" ", text)
    return text


def spanish_markers(text: str) -> list[str]:
    """Find the Spanish function words in prose. Quoted trigger terms do not count."""
    words = set(WORD_RE.findall(prose_only(text).lower()))
    return sorted(SPANISH_MARKERS & words)


def is_translation(path: Path) -> bool:
    """Report whether a file is an explicit translation, named for its language."""
    return bool(LANGUAGE_NAME_RE.search(path.stem) or LANGUAGE_NAME_RE.search(path.parent.name))


def check_language(skill: Skill) -> None:
    """Flag prose that is not in English, the one language this repository writes in."""
    for label, text in (("`description`", skill.description), ("SKILL.md", skill.body)):
        markers = spanish_markers(text)
        if len(markers) >= MIN_SPANISH_MARKERS:
            found = ", ".join(markers[:5])
            skill.warn(f"{label} reads as Spanish ({found}, ...) — everything here is written in English")

    references = skill.path / "references"
    for reference in sorted(references.rglob("*.md")) if references.is_dir() else []:
        if is_translation(reference):
            continue
        markers = spanish_markers(reference.read_text(encoding="utf-8"))
        if len(markers) >= MIN_SPANISH_MARKERS:
            rel = reference.relative_to(skill.path).as_posix()
            found = ", ".join(markers[:5])
            skill.warn(
                f"`{rel}` reads as Spanish ({found}, ...) — write it in English, or name the "
                "file for its language if it is an explicit translation"
            )


def local_links(text: str) -> list[str]:
    """Extract the relative markdown links, ignoring URLs and anchors."""
    targets = []
    for target in MD_LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "/")):
            continue
        targets.append(target)
    return targets


def check_links(skill: Skill) -> None:
    if "\\" in "".join(local_links(skill.body)):
        skill.error("use forward slashes in file paths — backslashes break on Unix")

    for target in local_links(skill.body):
        resolved = (skill.path / target).resolve()
        if not resolved.exists():
            skill.error(f"SKILL.md links to `{target}`, which does not exist")
            continue
        # Anthropic: keep references one level deep from SKILL.md, otherwise
        # Claude may only partially read the nested file.
        if resolved.suffix == ".md" and local_links(resolved.read_text(encoding="utf-8")):
            skill.warn(
                f"`{target}` links to further local files — keep references one level "
                "deep from SKILL.md"
            )

    references_dir = skill.path / "references"
    for reference in sorted(references_dir.glob("*.md")) if references_dir.is_dir() else []:
        rel = f"references/{reference.name}"
        text = reference.read_text(encoding="utf-8")
        if rel not in skill.body:
            skill.warn(f"`{rel}` is never linked from SKILL.md — Claude will not find it")
        # A partial read of a long file must still reveal everything it covers.
        if len(text.splitlines()) > 100 and "## Contents" not in text:
            skill.warn(f"`{rel}` is over 100 lines — add a `## Contents` table of contents at the top")

    scripts_dir = skill.path / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.iterdir()):
            if script.is_file() and script.name not in skill.body:
                skill.warn(f"`scripts/{script.name}` is never mentioned in SKILL.md")


def check_plugin_wiring(skill: Skill, plugins: list[Path], *, fix: bool) -> None:
    for plugin in plugins:
        link = plugin / "skills" / skill.folder
        expected = skill.path.resolve()
        if link.is_symlink() and link.resolve() == expected:
            continue
        if fix:
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.is_symlink() or link.exists():
                link.unlink()
            depth = len(link.parent.relative_to(plugin.parent.parent).parts)
            link.symlink_to(Path(*[".."] * depth) / "skills" / skill.folder)
            continue
        rel = link.relative_to(plugin.parent.parent)
        if not link.is_symlink() and link.exists():
            skill.error(f"`{rel}` is a copy, not a symlink to skills/{skill.folder}")
        elif link.is_symlink():
            skill.error(f"`{rel}` points to {link.resolve()} instead of skills/{skill.folder}")
        else:
            skill.error(f"missing plugin symlink `{rel}` — re-run with --fix")


def check_orphan_symlinks(repo_root: Path, plugins: list[Path], *, fix: bool) -> list[str]:
    problems: list[str] = []
    for plugin in plugins:
        links_dir = plugin / "skills"
        if not links_dir.is_dir():
            problems.append(f"`{links_dir.relative_to(repo_root)}` is missing")
            continue
        for entry in sorted(links_dir.iterdir()):
            if entry.name.startswith("."):
                continue
            if (repo_root / "skills" / entry.name).is_dir():
                continue
            if fix:
                entry.unlink()
                continue
            problems.append(
                f"orphan entry `{entry.relative_to(repo_root)}` has no matching skill — "
                "re-run with --fix"
            )
    return problems


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def force_utf8_output() -> None:
    """Re-encode stdout and stderr as UTF-8 so the status marks always print.

    A Windows console defaults to cp1252, where `✓` raises UnicodeEncodeError and the
    run dies on its first line of output rather than on a real finding. Streams that
    cannot be reconfigured, such as the `StringIO` the tests capture into, are left as
    they are.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    force_utf8_output()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("targets", nargs="*", help="skill folders to validate (default: every skill)")
    parser.add_argument("--repo-root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--fix", action="store_true", help="create missing plugin symlinks and drop orphans")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"error: {repo_root} is not a directory", file=sys.stderr)
        return 2

    skills = discover_skills(repo_root, args.targets)
    plugins = find_plugins(repo_root)

    print(f"Validating {len(skills)} skill(s) in {repo_root.name}\n")

    total_errors = 0
    total_warnings = 0

    for problem in check_orphan_symlinks(repo_root, plugins, fix=args.fix):
        print(f"  ✗ repo: {problem}")
        total_errors += 1

    seen: dict[str, str] = {}
    for skill in skills:
        if skill.skill_md.is_file():
            check_body(skill)
            check_name(skill)
            check_description(skill)
            check_language(skill)
            check_links(skill)
            check_plugin_wiring(skill, plugins, fix=args.fix)
            name = skill.frontmatter.get("name", "").strip()
            if name and name in seen:
                skill.error(f"duplicate skill name, already declared by `{seen[name]}`")
            elif name:
                seen[name] = skill.folder

        total_errors += len(skill.errors)
        total_warnings += len(skill.warnings)
        mark = "✗" if skill.errors else ("!" if skill.warnings else "✓")
        print(f"  {mark} {skill.folder}")
        for finding in skill.findings:
            print(f"      {finding.level}:   {finding.message}")

    print(f"\n{total_errors} error(s), {total_warnings} warning(s)")

    if total_errors or (args.strict and total_warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
