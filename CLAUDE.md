# somnio-ai-solutions

Repository of **generic, cross-area Claude Code skills** for Somnio Software.

Area-specific skills live in their own repositories (`somnio-engineering-ai`,
`somnio-finance-ai`, `somnio-pre-sales-ai`). If a skill only makes sense for one
area, it does not belong here.

## Layout

- `skills/<skill-name>/` — the source of truth for every skill.
- `plugins/somnio-ai-solutions/skills/<skill-name>` — a symlink to the skill folder.
  Never a copy.
- `templates/skill/` — the scaffold. Change it here, not per skill.
- `scripts/` — the harness (bash + `python3`, stdlib only, no dependencies).

## Adding or changing a skill

- Always scaffold with `make new-skill NAME=<skill-name> DESC="..."` — it creates the
  folder, the plugin symlink, and refreshes the README table in one step.
- Never hand-edit the Skills table in `README.md`; it is generated between the
  `<!-- skills:start -->` / `<!-- skills:end -->` markers. Run `make sync`.
- Run `make check` before committing. CI runs the same command.
- Follow `docs/skill-conventions.md` — it is the authoring standard, including the
  rules for writing the frontmatter `description`.

## Conventions

- Skill folder names are kebab-case and match the `name` in the frontmatter exactly.
- `SKILL.md` stays under ~500 lines. Long material goes in `references/`, executable
  steps in `scripts/`.
- Scripts in the harness must run with the system `python3` and `bash` — no
  third-party packages, no build step.
- Bump `plugins/somnio-ai-solutions/.claude-plugin/plugin.json` `version` when the set
  of skills changes.

## Language

- Skill and repository documentation is written in **English**.
- Respond to the user in the same language they write in. Supported: English and
  Spanish.
