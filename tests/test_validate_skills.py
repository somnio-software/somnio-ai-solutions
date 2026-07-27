"""Tests for the somnio-skill-verifier validator."""

from __future__ import annotations

import unittest
from pathlib import Path

from helpers import FakeRepo, run_main, skill_md, validate_skills as vs


def messages(skill) -> str:
    return " | ".join(f.message for f in skill.findings)


def check_all(skill, plugins=(), fix=False):
    vs.check_body(skill)
    vs.check_name(skill)
    vs.check_description(skill)
    vs.check_links(skill)
    vs.check_plugin_wiring(skill, list(plugins), fix)
    return skill


class ParseFrontmatterTests(unittest.TestCase):
    def test_folded_block_scalar_is_joined_with_spaces(self):
        data, body = vs.parse_frontmatter("---\nname: a\ndescription: >\n  one\n  two\n---\nbody\n")
        self.assertEqual(data["description"], "one two")
        self.assertEqual(body.strip(), "body")

    def test_literal_block_scalar_keeps_newlines(self):
        data, _ = vs.parse_frontmatter("---\ndescription: |\n  one\n  two\n---\n")
        self.assertEqual(data["description"], "one\ntwo")

    def test_quotes_are_stripped_and_unknown_lines_ignored(self):
        data, _ = vs.parse_frontmatter("---\nname: 'quoted'\n  stray line\nother: \"x\"\n---\n")
        self.assertEqual(data["name"], "quoted")
        self.assertEqual(data["other"], "x")

    def test_missing_or_unterminated_frontmatter_returns_empty(self):
        self.assertEqual(vs.parse_frontmatter("# no frontmatter\n"), ({}, "# no frontmatter\n"))
        self.assertEqual(vs.parse_frontmatter("---\nname: a\n")[0], {})
        self.assertEqual(vs.parse_frontmatter("")[0], {})


class NameTests(unittest.TestCase):
    def _skill(self, folder: str, name: str | None = None):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill(folder, link=False, name=name or folder)
            skill = vs.load_skill(path)
        vs.check_name(skill)
        return skill

    def test_valid_name_passes(self):
        self.assertEqual(self._skill("billing-report").findings, [])

    def test_name_must_match_folder(self):
        self.assertIn("does not match folder", messages(self._skill("billing-report", "other-name")))

    def test_name_must_be_kebab_case(self):
        self.assertIn("lowercase letters", messages(self._skill("Billing_Report")))

    def test_name_length_limit(self):
        long_name = "a" * (vs.MAX_NAME_LEN + 1)
        self.assertIn(f"the spec allows {vs.MAX_NAME_LEN}", messages(self._skill(long_name)))

    def test_reserved_words_are_rejected(self):
        self.assertIn("reserved word 'claude'", messages(self._skill("claude-helper")))
        self.assertIn("reserved word 'anthropic'", messages(self._skill("anthropic-tools")))

    def test_generic_names_warn(self):
        skill = self._skill("utils")
        self.assertEqual([f.level for f in skill.findings], [vs.WARNING])
        self.assertIn("too generic", messages(skill))

    def test_missing_name_is_an_error(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("x", link=False)
            (path / "SKILL.md").write_text("---\ndescription: d\n---\n# x\n", encoding="utf-8")
            skill = vs.load_skill(path)
        vs.check_name(skill)
        self.assertIn("missing `name`", messages(skill))


class DescriptionTests(unittest.TestCase):
    def _skill(self, description: str):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("billing-report", link=False, description=description)
            skill = vs.load_skill(path)
        vs.check_description(skill)
        return skill

    def test_good_description_passes(self):
        self.assertEqual(self._skill(
            "Generates the billing report as xlsx. Use this skill when the user asks "
            "for monthly invoicing. Do not use it for time entries."
        ).findings, [])

    def test_missing_description_is_an_error(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("x", link=False)
            (path / "SKILL.md").write_text("---\nname: x\n---\n# x\n", encoding="utf-8")
            skill = vs.load_skill(path)
        vs.check_description(skill)
        self.assertIn("missing `description`", messages(skill))

    def test_length_limit(self):
        skill = self._skill("Generates reports. Use when asked. " + "x" * vs.MAX_DESCRIPTION_LEN)
        self.assertIn(f"the spec allows {vs.MAX_DESCRIPTION_LEN}", messages(skill))

    def test_xml_tags_are_rejected(self):
        self.assertIn("XML tags", messages(self._skill("Generates <b>reports</b>. Use when asked for them.")))

    def test_template_placeholders_are_rejected(self):
        skill = self._skill("Does a thing. Use when <trigger> happens.")
        self.assertIn("template placeholders", messages(skill))

    def test_short_description_warns(self):
        self.assertIn("very short", messages(self._skill("Use when asked.")))

    def test_missing_trigger_phrase_warns(self):
        skill = self._skill("Generates the monthly billing report from Clockify exports as xlsx files.")
        self.assertIn("never says when to use", messages(skill))

    def test_first_person_warns(self):
        skill = self._skill("I can generate the billing report for you. Use this skill when asked for it.")
        self.assertIn("not third person", messages(skill))


class BodyTests(unittest.TestCase):
    def _skill(self, content: str):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("billing-report", link=False)
            (path / "SKILL.md").write_text(content, encoding="utf-8")
            skill = vs.load_skill(path)
        vs.check_body(skill)
        return skill

    def test_missing_frontmatter_is_an_error(self):
        self.assertIn("no YAML frontmatter", messages(self._skill("# no frontmatter\n")))

    def test_long_body_warns(self):
        body = "# Title\n" + "\n".join(f"line {i}" for i in range(vs.MAX_BODY_LINES + 5))
        self.assertIn("soft limit", messages(self._skill(skill_md("billing-report", body=body))))

    def test_missing_h1_warns(self):
        skill = self._skill(skill_md("billing-report", body="no title here\n"))
        self.assertIn("no H1 title", messages(skill))

    def test_authoring_notes_are_an_error(self):
        content = skill_md("billing-report", body="# T\n<!--\n  delete this comment before committing\n-->\n")
        self.assertIn("authoring notes", messages(self._skill(content)))

    def test_leftover_placeholders_are_an_error(self):
        content = skill_md("billing-report", body="# T\n\nTODO: write the workflow\n")
        self.assertIn("template placeholders", messages(self._skill(content)))


class LinkTests(unittest.TestCase):
    def test_broken_link_is_an_error(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nSee [gone](references/gone.md).\n")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("does not exist", messages(skill))

    def test_external_and_anchor_links_are_ignored(self):
        with FakeRepo(plugin=None) as repo:
            body = "# S\n\n[docs](https://example.com) [top](#section) [mail](mailto:a@b.c)\n"
            path = repo.add_skill("s", link=False, body=body)
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertEqual(skill.findings, [])

    def test_nested_reference_warns(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nSee [a](references/a.md).\n")
            (path / "references").mkdir()
            (path / "references" / "a.md").write_text("See [b](b.md).\n", encoding="utf-8")
            (path / "references" / "b.md").write_text("# B\n", encoding="utf-8")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("one level", messages(skill))

    def test_unlinked_reference_warns(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nNo links.\n")
            (path / "references").mkdir()
            (path / "references" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("never linked", messages(skill))

    def test_long_reference_without_contents_warns(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nSee [a](references/a.md).\n")
            (path / "references").mkdir()
            (path / "references" / "a.md").write_text("# A\n" + "text\n" * 120, encoding="utf-8")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("table of contents", messages(skill))

    def test_unmentioned_script_warns(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nNothing here.\n")
            (path / "scripts").mkdir()
            (path / "scripts" / "helper.py").write_text("print('hi')\n", encoding="utf-8")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("never mentioned", messages(skill))

    def test_backslash_paths_are_an_error(self):
        with FakeRepo(plugin=None) as repo:
            path = repo.add_skill("s", link=False, body="# S\n\nSee [a](references\\a.md).\n")
            skill = vs.load_skill(path)
            vs.check_links(skill)
        self.assertIn("forward slashes", messages(skill))


class PluginWiringTests(unittest.TestCase):
    def test_correct_symlink_passes(self):
        with FakeRepo() as repo:
            repo.add_skill("s")
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=False)
            self.assertEqual(skill.findings, [])

    def test_missing_symlink_is_an_error(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=False)
            self.assertIn("missing plugin symlink", messages(skill))

    def test_copy_instead_of_symlink_is_an_error(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            (repo.plugin_skills / "s").mkdir()
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=False)
            self.assertIn("is a copy", messages(skill))

    def test_symlink_to_the_wrong_target_is_an_error(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            repo.add_skill("other", link=False)
            repo.link("s", "../../../skills/other")
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=False)
            self.assertIn("points to", messages(skill))

    def test_fix_creates_the_symlink_with_the_right_depth(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=True)
            link = repo.plugin_skills / "s"
            self.assertEqual(skill.findings, [])
            self.assertTrue(link.is_symlink())
            self.assertEqual(str(Path(link.readlink())), "../../../skills/s")
            self.assertTrue((link / "SKILL.md").is_file())

    def test_fix_replaces_a_symlink_pointing_at_the_wrong_skill(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            repo.add_skill("other", link=False)
            repo.link("s", "../../../skills/other")
            skill = vs.load_skill(repo.skill_path("s"))
            vs.check_plugin_wiring(skill, vs.find_plugins(repo.root), fix=True)

            self.assertEqual(skill.findings, [])
            self.assertEqual(str(Path((repo.plugin_skills / "s").readlink())), "../../../skills/s")

    def test_repo_without_plugins_is_skipped(self):
        with FakeRepo(plugin=None) as repo:
            self.assertEqual(vs.find_plugins(repo.root), [])
            skill = vs.load_skill(repo.add_skill("s", link=False))
            vs.check_plugin_wiring(skill, [], fix=False)
            self.assertEqual(skill.findings, [])


class OrphanTests(unittest.TestCase):
    def test_orphan_symlink_is_reported(self):
        with FakeRepo() as repo:
            repo.add_skill("s")
            repo.link("ghost")
            problems = vs.check_orphan_symlinks(repo.root, vs.find_plugins(repo.root), fix=False)
        self.assertEqual(len(problems), 1)
        self.assertIn("ghost", problems[0])

    def test_fix_removes_the_orphan(self):
        with FakeRepo() as repo:
            repo.add_skill("s")
            repo.link("ghost")
            plugins = vs.find_plugins(repo.root)
            self.assertEqual(vs.check_orphan_symlinks(repo.root, plugins, fix=True), [])
            self.assertFalse((repo.plugin_skills / "ghost").is_symlink())

    def test_missing_skills_directory_in_plugin_is_reported(self):
        with FakeRepo() as repo:
            repo.add_skill("s", link=False)
            repo.plugin_skills.rmdir()
            problems = vs.check_orphan_symlinks(repo.root, vs.find_plugins(repo.root), fix=False)
        self.assertIn("is missing", problems[0])

    def test_hidden_entries_are_ignored(self):
        with FakeRepo() as repo:
            repo.add_skill("s")
            (repo.plugin_skills / ".gitkeep").write_text("", encoding="utf-8")
            self.assertEqual(vs.check_orphan_symlinks(repo.root, vs.find_plugins(repo.root), fix=False), [])


class DiscoveryTests(unittest.TestCase):
    def test_missing_skill_md_is_an_error(self):
        with FakeRepo(plugin=None) as repo:
            (repo.root / "skills" / "empty").mkdir()
            skill = vs.load_skill(repo.root / "skills" / "empty")
        self.assertIn("missing empty/SKILL.md", messages(skill))

    def test_discovery_skips_hidden_folders_and_files(self):
        with FakeRepo(plugin=None) as repo:
            repo.add_skill("s", link=False)
            (repo.root / "skills" / ".hidden").mkdir()
            (repo.root / "skills" / "loose.md").write_text("x", encoding="utf-8")
            found = vs.discover_skills(repo.root, [])
        self.assertEqual([s.folder for s in found], ["s"])

    def test_explicit_targets_win_over_discovery(self):
        with FakeRepo(plugin=None) as repo:
            repo.add_skill("a", link=False)
            repo.add_skill("b", link=False)
            found = vs.discover_skills(repo.root, [str(repo.skill_path("b"))])
        self.assertEqual([s.folder for s in found], ["b"])

    def test_repo_without_skills_directory_yields_nothing(self):
        with FakeRepo(plugin=None) as repo:
            (repo.root / "skills").rmdir()
            self.assertEqual(vs.discover_skills(repo.root, []), [])


class MainTests(unittest.TestCase):
    def test_clean_repo_exits_zero(self):
        with FakeRepo() as repo:
            repo.add_skill("billing-report")
            code, output = run_main(vs, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 0, output)
        self.assertIn("0 error(s), 0 warning(s)", output)

    def test_errors_exit_one(self):
        with FakeRepo() as repo:
            repo.add_skill("billing-report", link=False)
            code, output = run_main(vs, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 1)
        self.assertIn("✗ billing-report", output)

    def test_warnings_pass_unless_strict(self):
        with FakeRepo() as repo:
            weak = "Generates the report from Clockify exports as xlsx."
            repo.add_skill("billing-report", description=weak)
            self.assertEqual(run_main(vs, ["--repo-root", str(repo.root)])[0], 0)
            code, output = run_main(vs, ["--repo-root", str(repo.root), "--strict"])
        self.assertEqual(code, 1)
        self.assertIn("! billing-report", output)

    def test_duplicate_names_are_reported(self):
        with FakeRepo() as repo:
            repo.add_skill("a", name="a")
            repo.add_skill("b", name="a")
            code, output = run_main(vs, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 1)
        self.assertIn("duplicate skill name", output)

    def test_orphan_symlink_fails_the_run(self):
        with FakeRepo() as repo:
            repo.add_skill("billing-report")
            repo.link("ghost")
            code, output = run_main(vs, ["--repo-root", str(repo.root)])
        self.assertEqual(code, 1)
        self.assertIn("orphan entry", output)

    def test_fix_repairs_the_repository(self):
        with FakeRepo() as repo:
            repo.add_skill("billing-report", link=False)
            repo.link("ghost")
            code, _ = run_main(vs, ["--repo-root", str(repo.root), "--fix"])
        self.assertEqual(code, 0)

    def test_unknown_repo_root_exits_two(self):
        code, output = run_main(vs, ["--repo-root", "/nope/does/not/exist"])
        self.assertEqual(code, 2)
        self.assertIn("not a directory", output)

    def test_single_target_validation(self):
        with FakeRepo() as repo:
            repo.add_skill("a")
            repo.add_skill("b", link=False)
            code, output = run_main(vs, ["--repo-root", str(repo.root), str(repo.skill_path("a"))])
        self.assertEqual(code, 0, output)
        self.assertIn("Validating 1 skill(s)", output)


class RealRepositoryTests(unittest.TestCase):
    """The repository must always satisfy its own validator."""

    def test_this_repository_is_clean(self):
        from helpers import REPO_ROOT

        code, output = run_main(vs, ["--repo-root", str(REPO_ROOT), "--strict"])
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
