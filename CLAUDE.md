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

## Layout

- `skills/<skill-name>/` — the source of truth for every skill.
- `plugins/somnio-ai-solutions/skills/<skill-name>` — a **symlink** to the skill
  folder. Never a copy.
- `plugins/somnio-ai-solutions/.claude-plugin/plugin.json` — the plugin manifest.
- `.claude-plugin/marketplace.json` — makes the repo installable as a marketplace.

## Rules

- Scaffold every skill with `somnio-skill-creator`; do not create folders by hand.
- Never hand-edit the Skills table in `README.md`. It is generated between the
  `<!-- skills:start -->` / `<!-- skills:end -->` markers — run `make sync`.
- Run `make check` before committing. CI runs the same checks on every pull request.
- Skill folder names are kebab-case and match the `name` in the frontmatter exactly.
- `SKILL.md` stays under 500 lines. Long material goes in `references/`,
  deterministic steps in `scripts/`.
- Harness scripts run with the system `python3` and `bash` — stdlib only, no
  third-party packages, no build step.
- Bump `version` in `plugins/somnio-ai-solutions/.claude-plugin/plugin.json` when
  the set of skills changes.

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
