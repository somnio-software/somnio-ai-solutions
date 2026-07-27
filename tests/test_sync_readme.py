"""Tests for the README skills-table generator."""

from __future__ import annotations

import unittest

from helpers import FakeRepo, run_main, sync_readme as sr


class FrontmatterTests(unittest.TestCase):
    def test_reads_folded_descriptions(self):
        data = sr.parse_frontmatter("---\nname: a\ndescription: >\n  one\n  two\n---\nbody\n")
        self.assertEqual(data, {"name": "a", "description": "one two"})

    def test_reads_literal_descriptions_and_quotes(self):
        self.assertEqual(sr.parse_frontmatter("---\nd: |\n  one\n  two\n---\n")["d"], "one\ntwo")
        self.assertEqual(sr.parse_frontmatter("---\nn: \"quoted\"\nstray\n---\n")["n"], "quoted")

    def test_returns_empty_without_frontmatter(self):
        self.assertEqual(sr.parse_frontmatter("# title\n"), {})
        self.assertEqual(sr.parse_frontmatter("---\nname: a\n"), {})
        self.assertEqual(sr.parse_frontmatter(""), {})


class FirstSentenceTests(unittest.TestCase):
    def test_cuts_at_the_first_sentence(self):
        self.assertEqual(sr.first_sentence("Does a thing. Use when asked."), "Does a thing.")

    def test_keeps_a_single_sentence_whole(self):
        self.assertEqual(sr.first_sentence("Does a thing"), "Does a thing")

    def test_collapses_whitespace(self):
        self.assertEqual(sr.first_sentence("Does   a\n  thing"), "Does a thing")

    def test_does_not_cut_inside_a_filename(self):
        self.assertEqual(sr.first_sentence("Writes SKILL.md files. Then stops."), "Writes SKILL.md files.")


class TableTests(unittest.TestCase):
    def test_row_per_skill_sorted_by_folder(self):
        with FakeRepo() as repo:
            repo.add_skill("zebra", description="Zebra thing. Use when striped.")
            repo.add_skill("alpha", description="Alpha thing. Use when first.")
            table = sr.build_table(repo.root)

        rows = [line for line in table.splitlines() if line.startswith("| [")]
        self.assertEqual(len(rows), 2)
        self.assertIn("[`alpha`](./skills/alpha) | Alpha thing.", rows[0])
        self.assertIn("[`zebra`](./skills/zebra) | Zebra thing.", rows[1])

    def test_empty_repository_gets_a_placeholder(self):
        with FakeRepo() as repo:
            self.assertIn(sr.EMPTY_TABLE, sr.build_table(repo.root))

    def test_missing_skills_directory_gets_a_placeholder(self):
        with FakeRepo() as repo:
            (repo.root / "skills").rmdir()
            self.assertIn(sr.EMPTY_TABLE, sr.build_table(repo.root))

    def test_skill_without_description_is_still_listed(self):
        with FakeRepo() as repo:
            path = repo.add_skill("nameless")
            (path / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
            table = sr.build_table(repo.root)
        self.assertIn("_No description._", table)

    def test_skill_without_skill_md_is_still_listed(self):
        with FakeRepo() as repo:
            (repo.root / "skills" / "hollow").mkdir()
            self.assertIn("[`hollow`]", sr.build_table(repo.root))


class MainTests(unittest.TestCase):
    def test_writes_the_table_between_the_markers(self):
        with FakeRepo() as repo:
            repo.add_skill("alpha", description="Alpha thing. Use when first.")
            code, output = run_main(sr, ["--repo-root", str(repo.root)])

            self.assertEqual(code, 0, output)
            self.assertIn("updated", output)
            self.assertIn("[`alpha`](./skills/alpha)", repo.readme)
            self.assertNotIn("placeholder", repo.readme)
            self.assertIn("Tail content.", repo.readme)

    def test_is_idempotent(self):
        with FakeRepo() as repo:
            repo.add_skill("alpha", description="Alpha thing. Use when first.")
            run_main(sr, ["--repo-root", str(repo.root)])
            first = repo.readme
            code, output = run_main(sr, ["--repo-root", str(repo.root)])

            self.assertEqual(code, 0)
            self.assertIn("up to date", output)
            self.assertEqual(repo.readme, first)

    def test_check_fails_when_out_of_date_and_writes_nothing(self):
        with FakeRepo() as repo:
            repo.add_skill("alpha", description="Alpha thing. Use when first.")
            before = repo.readme
            code, output = run_main(sr, ["--repo-root", str(repo.root), "--check"])

            self.assertEqual(code, 1)
            self.assertIn("out of date", output)
            self.assertEqual(repo.readme, before)

    def test_check_passes_once_synced(self):
        with FakeRepo() as repo:
            repo.add_skill("alpha", description="Alpha thing. Use when first.")
            run_main(sr, ["--repo-root", str(repo.root)])
            self.assertEqual(run_main(sr, ["--repo-root", str(repo.root), "--check"])[0], 0)

    def test_missing_readme_fails(self):
        with FakeRepo(readme=False) as repo:
            code, output = run_main(sr, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 1)
        self.assertIn("not found", output)

    def test_readme_without_markers_fails(self):
        with FakeRepo() as repo:
            repo.write("README.md", "# No markers here\n")
            code, output = run_main(sr, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 1)
        self.assertIn("markers", output)


class RealRepositoryTests(unittest.TestCase):
    """The committed README must already match the skills on disk."""

    def test_this_repository_is_in_sync(self):
        from helpers import REPO_ROOT

        code, output = run_main(sr, ["--repo-root", str(REPO_ROOT), "--check"])
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
