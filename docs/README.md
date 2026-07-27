# Documentation

Everything about working in this repository. The [root README](../README.md) is
the index of Somnio's AI repositories and of the skills this one ships; the pages
here are the detail.

| Page | What it covers |
|:-----|:---------------|
| [Installation](installation.md) | Installing the plugin in Claude Code and in Claude Desktop (Cowork) |
| [Repository structure](repository-structure.md) | The tree, the `skills/` ↔ `plugins/` symlink contract, the Makefile |
| [Creating a skill](creating-skills.md) | Scaffolding a skill and writing it to the standard |
| [Importing a skill](importing-skills.md) | Adopting a skill copied from another repository with the `skill-importer` agent |
| [Testing](testing.md) | The suite, the 100% per-file coverage gate, and the pre-push hook |
| [Pipeline](pipeline.md) | What CI validates and how the plugin archive is built and committed |
| [Contributing](contributing.md) | Branch, review and merge workflow |

## Sources of truth

Two documents outrank everything here, and both live inside the skills so they
travel with them to the other `somnio-*-ai` repositories:

- [Authoring standard](../skills/somnio-skill-creator/references/authoring-standard.md)
  — how a skill is written. Based on Anthropic's Agent Skills specification.
- [Review rubric](../skills/somnio-skill-verifier/references/review-rubric.md) —
  how a skill is judged before merge.

Repository rules for Claude Code live in [`CLAUDE.md`](../CLAUDE.md), and the
Python rules for the harness scripts in [`.claude/rules`](../.claude/rules).
