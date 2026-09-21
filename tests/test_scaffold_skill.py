"""Tests for the somnio-skill-creator scaffolder."""

from __future__ import annotations

import unittest
from pathlib import Path

from helpers import FakeRepo, run_main, scaffold_skill as ss

DESCRIPTION = "Generates the monthly billing report. Use this skill when asked for invoicing."


class NameValidationTests(unittest.TestCase):
    def test_valid_names_are_accepted(self):
        for name in ("billing-report", "a", "report2", "somnio-skill-creator"):
            self.assertIsNone(ss.validate_name(name), name)

    def test_non_kebab_case_is_rejected(self):
        for name in ("Billing", "billing_report", "billing--report", "-billing", "billing "):
            self.assertIn("kebab-case", ss.validate_name(name) or "", name)

    def test_length_limit(self):
        self.assertIsNone(ss.validate_name("a" * ss.MAX_NAME_LEN))
        self.assertIn("the spec allows", ss.validate_name("a" * (ss.MAX_NAME_LEN + 1)))

    def test_reserved_words_are_rejected(self):
        self.assertIn("reserved word 'claude'", ss.validate_name("claude-helper"))
        self.assertIn("reserved word 'anthropic'", ss.validate_name("anthropic-tools"))

    def test_title_from_name(self):
        self.assertEqual(ss.title_from("somnio-skill-creator"), "Somnio Skill Creator")
        self.assertEqual(ss.title_from("report"), "Report")


class ScaffoldTests(unittest.TestCase):
    def scaffold(self, repo: FakeRepo, name: str, *extra: str):
        return run_main(ss, [name, "--repo-root", str(repo.root), *extra])

    def test_creates_the_skill_from_the_template(self):
        with FakeRepo() as repo:
            code, output = self.scaffold(repo, "billing-report", "--description", DESCRIPTION)
            skill_md = repo.skill_path("billing-report") / "SKILL.md"

            self.assertEqual(code, 0, output)
            self.assertTrue(skill_md.is_file())
            content = skill_md.read_text(encoding="utf-8")
            self.assertIn("name: billing-report", content)
            self.assertIn(DESCRIPTION, content)
            self.assertIn("# Billing Report", content)
            self.assertNotIn("{{", content)

    def test_creates_the_plugin_symlink(self):
        with FakeRepo() as repo:
            self.scaffold(repo, "billing-report")
            link = repo.plugin_skills / "billing-report"

            self.assertTrue(link.is_symlink())
            self.assertEqual(str(Path(link.readlink())), "../../../skills/billing-report")
            self.assertTrue((link / "SKILL.md").is_file())

    def test_syncs_the_readme_index(self):
        with FakeRepo() as repo:
            code, output = self.scaffold(repo, "billing-report", "--description", DESCRIPTION)
            self.assertEqual(code, 0, output)
            self.assertIn("[`billing-report`](./skills/billing-report)", repo.readme)

    def test_scaffolds_only_skill_md(self):
        # The template ships no empty scripts/ or references/ folders: the author
        # creates them only if the skill actually needs them.
        with FakeRepo() as repo:
            self.scaffold(repo, "billing-report")
            skill = repo.skill_path("billing-report")
            self.assertEqual([p.name for p in skill.iterdir()], ["SKILL.md"])

    def test_default_description_is_a_placeholder_the_validator_rejects(self):
        from helpers import validate_skills as vs

        with FakeRepo() as repo:
            self.scaffold(repo, "billing-report")
            skill = vs.load_skill(repo.skill_path("billing-report"))
            vs.check_description(skill)
        self.assertTrue(any("placeholder" in f.message for f in skill.findings))

    def test_refuses_an_existing_skill(self):
        with FakeRepo() as repo:
            repo.add_skill("billing-report")
            code, output = self.scaffold(repo, "billing-report")
        self.assertEqual(code, 1)
        self.assertIn("already exists", output)

    def test_refuses_an_invalid_name(self):
        with FakeRepo() as repo:
            code, output = self.scaffold(repo, "Billing_Report")
            self.assertEqual(code, 1)
            self.assertIn("kebab-case", output)
            self.assertFalse((repo.root / "skills" / "Billing_Report").exists())

    def test_refuses_a_missing_repo_root(self):
        code, output = run_main(ss, ["billing-report", "--repo-root", "/nope/does/not/exist"])
        self.assertEqual(code, 1)
        self.assertIn("not a directory", output)

    def test_warns_when_the_repository_has_no_plugin(self):
        with FakeRepo(plugin=None) as repo:
            code, output = self.scaffold(repo, "billing-report")
        self.assertEqual(code, 0)
        self.assertIn("no plugin found", output)

    def test_links_into_every_plugin(self):
        with FakeRepo() as repo:
            second = repo.root / "plugins" / "other-plugin"
            (second / ".claude-plugin").mkdir(parents=True)
            (second / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")

            self.scaffold(repo, "billing-report")

            self.assertTrue((repo.plugin_skills / "billing-report").is_symlink())
            self.assertTrue((second / "skills" / "billing-report").is_symlink())

    def test_works_without_a_readme(self):
        with FakeRepo(readme=False) as repo:
            code, output = self.scaffold(repo, "billing-report")
        self.assertEqual(code, 0, output)
        self.assertNotIn("skills table regenerated", output)

    def test_replaces_a_stale_symlink(self):
        with FakeRepo() as repo:
            repo.link("billing-report", "../../../skills/gone")
            self.scaffold(repo, "billing-report")
            link = repo.plugin_skills / "billing-report"
            self.assertEqual(str(Path(link.readlink())), "../../../skills/billing-report")


class RenderTemplateTests(unittest.TestCase):
    def test_walks_directories_and_replaces_placeholders_in_every_file(self):
        with FakeRepo(plugin=None) as repo:
            target = repo.root / "rendered"
            (target / "nested").mkdir(parents=True)
            (target / "SKILL.md").write_text("name: {{SKILL_NAME}}\n# {{SKILL_TITLE}}\n", encoding="utf-8")
            (target / "nested" / "extra.md").write_text("{{SKILL_DESCRIPTION}}\n", encoding="utf-8")

            ss.render_template(target, "billing-report", "Generates it.")

            self.assertEqual(
                (target / "SKILL.md").read_text(encoding="utf-8"),
                "name: billing-report\n# Billing Report\n",
            )
            self.assertEqual((target / "nested" / "extra.md").read_text(encoding="utf-8"), "Generates it.\n")

    def test_missing_template_is_reported(self):
        original = ss.TEMPLATE_DIR
        ss.TEMPLATE_DIR = Path("/nope/does/not/exist")
        try:
            with FakeRepo() as repo:
                code, output = run_main(ss, ["billing-report", "--repo-root", str(repo.root)])
                self.assertEqual(code, 1)
                self.assertIn("template not found", output)
                self.assertFalse(repo.skill_path("billing-report").exists())
        finally:
            ss.TEMPLATE_DIR = original


class ScaffoldedSkillTests(unittest.TestCase):
    """A freshly scaffolded skill must fail validation until it is written."""

    def test_template_output_is_rejected_until_the_notes_are_removed(self):
        from helpers import validate_skills as vs

        with FakeRepo() as repo:
            run_main(ss, ["billing-report", "--repo-root", str(repo.root), "--description", DESCRIPTION])
            code, output = run_main(vs, ["--repo-root", str(repo.root)])
            self.assertEqual(code, 1)
            self.assertIn("authoring notes", output)

            skill_md = repo.skill_path("billing-report") / "SKILL.md"
            content = skill_md.read_text(encoding="utf-8")
            start, _, rest = content.partition("<!--")
            skill_md.write_text(start + rest.partition("-->")[2], encoding="utf-8")

            code, output = run_main(vs, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
