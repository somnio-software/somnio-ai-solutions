"""Enforces the Python rules in .claude/rules/python that a tool would normally check.

This repository takes no third-party dependency, so there is no Ruff to run the
gate. These tests are the gate.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

from helpers import REPO_ROOT

MAX_LINE_LENGTH = 110
LOCAL_MODULES = {"helpers", "validate_skills", "scaffold_skill", "sync_readme", "run_tests"}

PYTHON_FILES = sorted(
    path
    for path in REPO_ROOT.rglob("*.py")
    if ".git" not in path.parts and "__pycache__" not in path.parts
)
SKILL_SCRIPTS = sorted(REPO_ROOT.glob("skills/*/scripts/*.py"))


class InventoryTests(unittest.TestCase):
    def test_the_repository_has_python_to_check(self):
        self.assertTrue(PYTHON_FILES)
        self.assertTrue(SKILL_SCRIPTS)


class LineLengthTests(unittest.TestCase):
    def test_no_line_exceeds_the_limit(self):
        offenders = [
            f"{path.relative_to(REPO_ROOT)}:{number} ({len(line)} cols)"
            for path in PYTHON_FILES
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
            if len(line) > MAX_LINE_LENGTH
        ]
        self.assertEqual(offenders, [], f"lines over {MAX_LINE_LENGTH} columns")

    def test_no_tabs_for_indentation(self):
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in PYTHON_FILES
            if any(line.startswith("\t") for line in path.read_text(encoding="utf-8").splitlines())
        ]
        self.assertEqual(offenders, [])


class DocstringTests(unittest.TestCase):
    def test_every_module_has_a_docstring(self):
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in PYTHON_FILES
            if not ast.get_docstring(ast.parse(path.read_text(encoding="utf-8")))
        ]
        self.assertEqual(offenders, [])

    def test_skill_scripts_document_usage_and_exit_codes(self):
        for path in SKILL_SCRIPTS:
            with self.subTest(script=path.name):
                docstring = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
                self.assertIn("Usage:", docstring)
                self.assertIn("Exit codes:", docstring)


class DependencyTests(unittest.TestCase):
    """The zero-dependency guarantee: skills must run with a bare python3."""

    def test_every_import_is_stdlib_or_local(self):
        offenders: list[str] = []
        for path in PYTHON_FILES:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    roots = [(node.module or "").split(".")[0]]
                else:
                    continue
                offenders.extend(
                    f"{path.relative_to(REPO_ROOT)}: {root}"
                    for root in roots
                    if root and root not in sys.stdlib_module_names and root not in LOCAL_MODULES
                )
        self.assertEqual(offenders, [], "third-party imports are forbidden in this repository")


class ScriptContractTests(unittest.TestCase):
    """Every skill script is a CLI: importable, with main() and a guard."""

    def test_scripts_are_executable_with_a_shebang(self):
        for path in SKILL_SCRIPTS:
            with self.subTest(script=path.name):
                self.assertTrue(path.stat().st_mode & 0o111, "missing the executable bit")
                first_line = path.read_text(encoding="utf-8").splitlines()[0]
                self.assertEqual(first_line, "#!/usr/bin/env python3")

    def test_scripts_expose_main_and_the_guard(self):
        for path in SKILL_SCRIPTS:
            with self.subTest(script=path.name):
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source)
                functions = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                self.assertIn("main", functions)
                self.assertIn('if __name__ == "__main__":', source)

    def test_scripts_have_no_side_effects_at_import_time(self):
        allowed = (
            ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.Assign,
            ast.AnnAssign, ast.Expr, ast.If,
        )
        for path in SKILL_SCRIPTS:
            with self.subTest(script=path.name):
                for node in ast.parse(path.read_text(encoding="utf-8")).body:
                    self.assertIsInstance(node, allowed)
                    if isinstance(node, ast.If):
                        # The only module-level `if` allowed is the __main__ guard.
                        self.assertIn("__name__", ast.dump(node.test))


if __name__ == "__main__":
    unittest.main()
