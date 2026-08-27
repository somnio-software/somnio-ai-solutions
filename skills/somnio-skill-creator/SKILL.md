---
name: somnio-skill-creator
description: >
  Creates a new Claude Code skill in a Somnio repository — scaffolds the folder,
  writes SKILL.md to Anthropic's spec, wires the plugin symlink, and updates the
  README index. Use this skill when the user asks to create, add, scaffold, write
  or start a new skill, a SKILL.md, or an agent skill, in any somnio-*-ai
  repository, including the Spanish phrasings "crear una skill", "armar una
  skill" or "agregar una skill nueva". Do not use it to review or fix an existing
  skill — that is somnio-skill-verifier — and do not use it to adopt a skill
  copied from another repository, which is the skill-importer agent.
---

# Somnio Skill Creator

Creates skills that Claude actually triggers and follows. Somnio has one skill
repository per area; this skill keeps them all to the same standard.

## Workflow

Copy this checklist and tick items off as you go:

```
- [ ] Step 1: Frame the skill
- [ ] Step 2: Confirm the repository
- [ ] Step 3: Scaffold
- [ ] Step 4: Write the description
- [ ] Step 5: Write the body
- [ ] Step 6: Validate and report
```

### Step 1 — Frame the skill

Before writing anything, establish four things. Ask with `AskUserQuestion`, one
question at a time, only for what the user has not already said:

1. **The job.** One sentence, one job. If the answer contains "and" joining two
   unrelated outcomes, it is two skills — say so and propose splitting.
2. **The triggers.** The words a user would really type when they need it, in
   both English and Spanish if the team uses both.
3. **The non-triggers.** The neighbouring skill it could be confused with.
4. **The freedom level.** Fragile and must be identical every time (a script), or
   judgement-driven (prose instructions)? See
   [references/authoring-standard.md](references/authoring-standard.md).

Then check the skill does not already exist: read the README index, or run
`ls skills/`. If something close exists, propose extending it instead.

### Step 2 — Confirm the repository

Skills are area-scoped. Confirm the current repository is the right home:

| If the skill serves | It belongs in |
|:--------------------|:--------------|
| Every area | `somnio-ai-solutions` |
| Engineering (Tech Leads, engineering teams) | `somnio-engineering-ai` |
| Engineering management / QA management only | `somnio-em-ai` |
| Finance only | `somnio-finance-ai` |
| Pre-sales only | `somnio-pre-sales-ai` |
| Sales only | `somnio-sales-ai` |
| Marketing only | `somnio-marketing-ai` |
| HR only | `somnio-hr-ai` |
| Product only | `somnio-product-ai` |

If the user is in the wrong repository, say so before scaffolding.

### Step 3 — Scaffold

Run from the repository root:

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --description "What it does. Use this skill when ..."
```

The script creates `skills/<skill-name>/` from
[assets/skill-template/SKILL.md](assets/skill-template/SKILL.md), symlinks it
into every plugin under `plugins/`, and refreshes the README table. It refuses
names that are not kebab-case, exceed 64 characters, or contain the reserved
words that Anthropic's spec forbids.

Working in another repository? Add `--repo-root ../somnio-finance-ai`.

### Step 4 — Write the description

This is the highest-leverage step. The description is the only text Claude reads
when deciding whether to load the skill, so a great skill with a vague
description never runs.

Write it in third person, stating **what it does** and **when to use it**, with
concrete trigger terms and at least one explicit non-trigger:

```yaml
description: >
  Generates the monthly billing report from Clockify exports and writes it as
  .xlsx. Use this skill when the user asks for the billing report, monthly
  invoicing, or hours-to-invoice reconciliation. Do not use it for individual
  time entries — that is clockify-tracker.
```

Full rules, limits, and the good-versus-bad examples are in
[references/authoring-standard.md](references/authoring-standard.md).

### Step 5 — Write the body

Fill in the template and delete its authoring notes. Hold to these:

- **Assume Claude is smart.** Only add what it does not already know. Every
  paragraph must justify its token cost.
- **Under 500 lines.** Longer material goes to `references/`, one level deep from
  SKILL.md, linked explicitly so Claude can find it.
- **Scripts over prose for deterministic work.** A script is more reliable than
  regenerated code, costs no context to run, and produces the same result every
  time. Say plainly whether Claude should *run* the script or *read* it.
- **Give a default, not a menu.** One recommended path plus an escape hatch.
- **Consistent terminology.** One term per concept, throughout.
- **No time-sensitive statements.** Put superseded behaviour under an "old
  patterns" section instead.
- **Forward slashes** in every path, and no dates or versions that will rot.

Delete `scripts/` and `references/` if the skill does not use them.

### Step 6 — Validate and report

```bash
python3 skills/somnio-skill-verifier/scripts/validate_skills.py skills/<skill-name>
```

Fix every error and re-run until it is clean. Then hand the skill to
`somnio-skill-verifier` for the qualitative review before opening the pull
request.

Finally, tell the user: what was created, what the description triggers on, and
that the plugin `.zip` is rebuilt by CI on merge — they do not build it by hand.

## Scripts

| Script | Purpose |
|:-------|:--------|
| `scripts/scaffold_skill.py` | Creates the skill folder, plugin symlinks, and README row. Run it. |
| `scripts/sync_readme.py` | Regenerates the README skills table on its own. Run it after renaming or deleting a skill. |

## Repository layout

How `skills/`, `plugins/`, the symlinks, and the packaging pipeline fit together:
[references/repository-layout.md](references/repository-layout.md).

## Guardrails

- Never hand-write a skill folder — scaffold it, so every repository stays identical.
- Never edit the README skills table by hand; it is generated between markers.
- Never commit a skill that still contains the template's authoring notes.
- Never create a plugin symlink as a copy of the skill folder.
