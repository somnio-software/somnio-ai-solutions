"""Keeps the documentation index honest: no broken links, no unlisted pages."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from helpers import REPO_ROOT

DOCS_DIR = REPO_ROOT / "docs"
ROOT_README = REPO_ROOT / "README.md"
DOCS_INDEX = DOCS_DIR / "README.md"

MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

# Markdown files whose links must resolve. Skill files are covered by the
# validator itself, so this is the documentation outside skills/.
DOCUMENTATION = sorted(
    [ROOT_README, REPO_ROOT / "CLAUDE.md", *DOCS_DIR.glob("*.md"), *(REPO_ROOT / ".claude").rglob("*.md")]
)


def local_links(text: str) -> list[str]:
    """Relative markdown link targets, ignoring URLs and bare anchors."""
    targets = []
    for target in MD_LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("mailto:", "/")):
            continue
        targets.append(target)
    return targets


class LinkTests(unittest.TestCase):
    def test_every_relative_link_resolves(self):
        broken = [
            f"{path.relative_to(REPO_ROOT)} -> {target}"
            for path in DOCUMENTATION
            for target in local_links(path.read_text(encoding="utf-8"))
            if not (path.parent / target).exists()
        ]
        self.assertEqual(broken, [])

    def test_no_backslash_paths(self):
        offenders = [
            f"{path.relative_to(REPO_ROOT)} -> {target}"
            for path in DOCUMENTATION
            for target in local_links(path.read_text(encoding="utf-8"))
            if "\\" in target
        ]
        self.assertEqual(offenders, [])


class IndexTests(unittest.TestCase):
    def test_the_root_readme_links_to_the_docs_index(self):
        self.assertIn("./docs", ROOT_README.read_text(encoding="utf-8"))

    def test_the_root_readme_indexes_every_area_repository(self):
        # The repository index is the one section the README must always carry.
        readme = ROOT_README.read_text(encoding="utf-8")
        for repository in (
            "somnio-ai-solutions",
            "somnio-engineering-ai",
            "somnio-finance-ai",
            "somnio-pre-sales-ai",
        ):
            with self.subTest(repository=repository):
                self.assertIn(f"github.com/somnio-software/{repository}", readme)

    def test_every_docs_page_is_listed_in_both_indexes(self):
        root_readme = ROOT_README.read_text(encoding="utf-8")
        docs_index = DOCS_INDEX.read_text(encoding="utf-8")
        pages = [page for page in sorted(DOCS_DIR.glob("*.md")) if page != DOCS_INDEX]

        self.assertTrue(pages, "docs/ has no pages")
        for page in pages:
            with self.subTest(page=page.name):
                self.assertIn(f"./docs/{page.name}", root_readme)
                self.assertIn(f"({page.name})", docs_index)

    def test_every_docs_page_has_a_title(self):
        for page in sorted(DOCS_DIR.glob("*.md")):
            with self.subTest(page=page.name):
                first = page.read_text(encoding="utf-8").splitlines()[0]
                self.assertTrue(first.startswith("# "), f"{page.name} has no H1 title")


if __name__ == "__main__":
    unittest.main()
