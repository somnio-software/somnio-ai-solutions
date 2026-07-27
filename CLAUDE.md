# somnio-ai-solutions

Repository of **generic, cross-area Claude Code skills** for Somnio Software.

Area-specific skills live in their own repositories (`somnio-engineering-ai`,
`somnio-finance-ai`, `somnio-pre-sales-ai`). If a skill only makes sense for one
area, it does not belong here.

## The harness is made of skills

There is no separate tooling directory. Creating and reviewing skills is done by
the skills in this repository:

- **`somnio-skill-creator`** — scaffolds a new skill, wires the plugin symlink,
  updates the README index. Use it instead of hand-creating folders, in this repo
  and in the area repos (`--repo-root ../somnio-finance-ai`).
- **`somnio-skill-verifier`** — validates skills against Anthropic's spec and
  Somnio's standard, and reviews them qualitatively before merge.

The authoring standard lives in
`skills/somnio-skill-creator/references/authoring-standard.md`. It is the single
source of truth for every area repository — update it there, never fork it.

## Agents

- **`skill-importer`** (`.claude/agents/skill-importer.md`) — adopts a skill
  copied from another repository, URL or machine: it asks for the source and
  waits for it, then reviews, corrects and reformats the skill to the standard
  and leaves the validator clean. Use it instead of adapting an import by hand.
  It drives the skills above; it never reimplements their checks.

## Layout

- `skills/<skill-name>/` — the source of truth for every skill.
- `plugins/somnio-ai-solutions/skills/<skill-name>` — a **symlink** to the skill
  folder. Never a copy.
- `plugins/somnio-ai-solutions/.claude-plugin/plugin.json` — the plugin manifest.
- `.claude-plugin/marketplace.json` — makes the repo installable as a marketplace.
- `tests/` — the harness test suite and its coverage gate.
- `.githooks/` — versioned git hooks; enable them with `make hooks`.

## Rules

- Scaffold every skill with `somnio-skill-creator`; do not create folders by hand.
- Never hand-edit the Skills table in `README.md`. It is generated between the
  `<!-- skills:start -->` / `<!-- skills:end -->` markers — run `make sync`.
- Run `make check` before committing. CI and the pre-push hook run the same gates.
- Skill folder names are kebab-case and match the `name` in the frontmatter exactly.
- `SKILL.md` stays under 500 lines. Long material goes in `references/`,
  deterministic steps in `scripts/`.
- Harness scripts run with the system `python3` and `bash` — stdlib only, no
  third-party packages, no build step.
- Bump `version` in `plugins/somnio-ai-solutions/.claude-plugin/plugin.json` when
  the set of skills changes.

## Tests

- Every script under `skills/*/scripts/` is covered by `tests/`, and the gate is
  **100% line coverage per file** — not an aggregate average. It does not go down:
  when a line is hard to reach, either test it or delete it.
- Run them with `make test` (fast) or `make coverage` (with the gate).
- The suite uses stdlib `unittest` and real temporary repositories. No pytest, no
  mocking library, no third-party import anywhere — `tests/test_code_style.py`
  enforces that, along with the line limit and the script CLI contract.
- Enable the pre-push hook once per clone with `make hooks`. It runs validation,
  the README sync check, and the tests with the coverage gate before every push.

## Plugins

**The `.zip` is built by CI, not by hand.** The `skills` workflow rebuilds
`plugins/somnio-ai-solutions.zip` and commits it whenever anything under
`skills/` or `plugins/` lands on `main`. Do not commit a locally built archive.

When you do need to build one locally (debugging a Cowork upload), run it from
the `plugins/` directory so the archive contains the plugin folder at its root:

```bash
cd plugins
zip -r <plugin-name>.zip <plugin-name>/ \
  --exclude "*.DS_Store" \
  --exclude "*/.venv/*" \
  --exclude "*/.ruff_cache/*" \
  --exclude "*/__pycache__/*" \
  --exclude "*/.git/*"
```

Save the resulting `.zip` alongside the plugin directory (e.g.
`plugins/somnio-ai-solutions.zip`). `zip` dereferences the skill symlinks, so the
archive is self-contained — verify with `unzip -l` that every skill's `SKILL.md`
is inside. `make zip` runs exactly this command after validating.

## Language

- Skill and repository documentation is written in **English**.
- Respond to the user in the same language they write in. Supported: English and
  Spanish.

## Python rules

Adapted from `somnio-ai-tools/agent-rules`; see `.claude/rules/README.md` for what
was changed and why.

@.claude/rules/python/code-style.md
@.claude/rules/python/module-structure.md
@.claude/rules/python/function-design.md
@.claude/rules/python/error-handling.md
@.claude/rules/python/typing.md
@.claude/rules/python/testing-unit.md
