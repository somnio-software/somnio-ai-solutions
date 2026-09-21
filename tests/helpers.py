"""Shared fixtures for the harness tests: module loading and throwaway repos."""

from __future__ import annotations

import importlib.util
import io
import contextlib
import shutil
import sys
import tempfile
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parent.parent

CREATOR_SCRIPTS = REPO_ROOT / "skills" / "somnio-skill-creator" / "scripts"
VERIFIER_SCRIPTS = REPO_ROOT / "skills" / "somnio-skill-verifier" / "scripts"

VALID_DESCRIPTION = (
    "Generates the monthly billing report from Clockify exports and writes it as "
    "xlsx. Use this skill when the user asks for the billing report or monthly "
    "invoicing. Do not use it for single time entries."
)

README_TEMPLATE = """# Fake repo

<!-- skills:start -->

placeholder

<!-- skills:end -->

Tail content.
"""


def load_module(path: Path, name: str) -> ModuleType:
    """Import a script by path so tests exercise it in-process (and traced)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validate_skills = load_module(VERIFIER_SCRIPTS / "validate_skills.py", "validate_skills")
scaffold_skill = load_module(CREATOR_SCRIPTS / "scaffold_skill.py", "scaffold_skill")
sync_readme = load_module(CREATOR_SCRIPTS / "sync_readme.py", "sync_readme")


def skill_md(name: str, description: str = VALID_DESCRIPTION, body: str | None = None) -> str:
    body = body if body is not None else f"# {name}\n\nDoes the thing.\n"
    return f"---\nname: {name}\ndescription: >\n  {description}\n---\n\n{body}"


class FakeRepo:
    """A disposable repository with the Somnio layout, for end-to-end assertions."""

    def __init__(self, plugin: str | None = "test-plugin", readme: bool = True) -> None:
        self._tmp = tempfile.mkdtemp(prefix="somnio-skills-test-")
        self.root = Path(self._tmp).resolve()
        (self.root / "skills").mkdir()
        self.plugin_name = plugin
        if plugin:
            plugin_dir = self.root / "plugins" / plugin
            (plugin_dir / ".claude-plugin").mkdir(parents=True)
            (plugin_dir / ".claude-plugin" / "plugin.json").write_text('{"name": "test"}\n', encoding="utf-8")
            (plugin_dir / "skills").mkdir()
        if readme:
            (self.root / "README.md").write_text(README_TEMPLATE, encoding="utf-8")

    # -- construction ----------------------------------------------------- #

    def add_skill(self, folder: str, *, link: bool = True, **kwargs) -> Path:
        path = self.root / "skills" / folder
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(skill_md(kwargs.pop("name", folder), **kwargs), encoding="utf-8")
        if link and self.plugin_name:
            self.link(folder)
        return path

    def link(self, folder: str, target: str | None = None) -> Path:
        link = self.plugin_skills / folder
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target or f"../../../skills/{folder}")
        return link

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    # -- accessors -------------------------------------------------------- #

    @property
    def plugin_skills(self) -> Path:
        assert self.plugin_name
        return self.root / "plugins" / self.plugin_name / "skills"

    @property
    def readme(self) -> str:
        return (self.root / "README.md").read_text(encoding="utf-8")

    def skill_path(self, folder: str) -> Path:
        return self.root / "skills" / folder

    # -- lifecycle -------------------------------------------------------- #

    def cleanup(self) -> None:
        shutil.rmtree(self._tmp, ignore_errors=True)

    def __enter__(self) -> "FakeRepo":
        return self

    def __exit__(self, *_exc) -> None:
        self.cleanup()


def run_main(module: ModuleType, argv: list[str]) -> tuple[int, str]:
    """Call a script's `main()` with the given arguments, capturing its output."""
    stream = io.StringIO()
    original = sys.argv
    sys.argv = [module.__name__, *argv]
    try:
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            code = module.main()
    except SystemExit as exit_error:  # argparse errors
        code = int(exit_error.code or 0)
    finally:
        sys.argv = original
    return code, stream.getvalue()
