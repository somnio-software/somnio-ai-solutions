# Skill Conventions

The authoring standard for every skill in this repository. The validator
(`make validate`) enforces the mechanical rules; the rest is review criteria.

---

## 1. Anatomy

```
skills/<skill-name>/
├── SKILL.md          # required — frontmatter + instructions
├── scripts/          # optional — deterministic helpers the skill runs
├── references/       # optional — long material, read only when needed
└── assets/           # optional — templates, images, fixtures
```

One skill = one job. If a folder does two unrelated things, it is two skills.

---

## 2. Naming

| Rule | Enforced |
|:-----|:---------|
| Folder name is kebab-case (`a-z`, `0-9`, single dashes) | ✅ error |
| Frontmatter `name` matches the folder name exactly | ✅ error |
| Name is 64 characters or fewer | ✅ error |
| Name reads as what the skill *does*, not how it works | review |

Cross-area skills carry the `somnio-` prefix when they act on Somnio's own
tooling (e.g. `somnio-skill-creator`, `somnio-skill-verifier`).

---

## 3. The `description` is the product

Claude never reads `SKILL.md` until it decides to load the skill, and that
decision is made **from the description alone**. A perfect skill with a vague
description never runs.

Write it:

- in **third person** — "Creates ...", "Reviews ...", not "I will ...";
- stating **what it does** *and* **when to use it**;
- with the **words a user would actually type** — synonyms, file formats, tool
  names, the Spanish and English terms if both are used in practice;
- with explicit **non-triggers** when the skill is easy to confuse with another.

```yaml
---
name: somnio-skill-verifier
description: >
  Reviews an existing Claude Code skill against Somnio's authoring standard and
  reports what to fix. Use this skill when the user asks to review, verify, audit
  or improve a skill, or mentions SKILL.md quality. Do not use it to create a new
  skill from scratch — that is somnio-skill-creator.
---
```

Hard limit: 1024 characters (enforced). Under 40 characters is flagged as a
warning — it is almost never enough to trigger reliably.

---

## 4. The body

- Keep `SKILL.md` under **~500 lines** (warning above that). Claude loads the whole
  file into context once triggered.
- Write **imperative instructions**, not narrative. "Ask for X with
  `AskUserQuestion`", not "the skill will probably want to know X".
- Structure the workflow in numbered phases with clear exit conditions.
- State the **output** explicitly: format, location, filename.
- Add **guardrails**: what to never invent, when to ask before overwriting, what to
  report when a step is skipped.
- Push anything long — rubrics, question banks, templates, examples — into
  `references/` and link to it, so it is loaded only when needed.

---

## 5. Scripts

- Prefer a script over prose whenever the step is deterministic (parsing,
  formatting, file generation). Models drift; scripts do not.
- Use the system `python3` (stdlib only) or `bash`. If a skill genuinely needs
  third-party packages, ship a `requirements.txt` inside the skill folder and
  document the setup in its `SKILL.md`.
- Scripts must be runnable from the repository root and fail loudly.

---

## 6. Plugin wiring

Every skill needs a symlink so the plugin picks it up:

```bash
ln -s ../../../skills/<skill-name> plugins/somnio-ai-solutions/skills/<skill-name>
```

`make new-skill` does this for you. `make validate` fails on a missing symlink, a
symlink pointing somewhere else, or an orphan symlink with no matching skill.

---

## 7. Checklist before opening a PR

- [ ] `make check` passes.
- [ ] The authoring notes comment was deleted from `SKILL.md`.
- [ ] The description names concrete triggers *and* at least one non-trigger.
- [ ] The skill was tried end-to-end in Claude Code at least once.
- [ ] Nothing area-specific leaked in — this repo is cross-area only.
- [ ] `plugin.json` `version` bumped if the set of skills changed.
