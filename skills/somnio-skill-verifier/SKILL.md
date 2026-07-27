---
name: somnio-skill-verifier
description: >
  Reviews existing Claude Code skills against Anthropic's spec and Somnio's
  standard, then reports what to fix — frontmatter limits, description quality,
  progressive disclosure, script hygiene, and plugin symlinks. Use this skill
  when the user asks to review, verify, validate, audit, lint or improve a skill
  or a SKILL.md, or before merging skill changes in any somnio-*-ai repository,
  including the Spanish phrasings "revisar una skill", "validar la skill" or
  "auditar las skills". Do not use it to create a new skill from scratch — that is
  somnio-skill-creator — and do not use it to adopt a skill copied from another
  repository, which is the skill-importer agent.
---

# Somnio Skill Verifier

Two passes: a script catches everything mechanical, then you judge what a script
cannot — whether the skill would actually trigger, and whether Claude could
follow it without the author in the room.

## Workflow

Copy this checklist and tick items off as you go:

```
- [ ] Step 1: Run the validator
- [ ] Step 2: Fix or explain every error
- [ ] Step 3: Review against the rubric
- [ ] Step 4: Trigger test
- [ ] Step 5: Report
```

### Step 1 — Run the validator

From the repository root:

```bash
python3 skills/somnio-skill-verifier/scripts/validate_skills.py
```

| Argument | Effect |
|:---------|:-------|
| `skills/<skill-name>` | Validate one skill instead of all of them |
| `--repo-root ../somnio-finance-ai` | Validate another repository |
| `--strict` | Treat warnings as failures, as CI does on release |
| `--fix` | Recreate missing plugin symlinks and drop orphans |

It checks the frontmatter limits, kebab-case and reserved words, the description
heuristics, body length, broken or nested references, template leftovers, and the
plugin symlinks.

### Step 2 — Fix or explain every error

Errors are violations of the specification or of repository structure — fix them.
Apply `--fix` for symlink problems; edit `SKILL.md` for the rest. Re-run until
the output is clean.

Warnings are judgement calls. Fix them or state in the report why the skill is
better off ignoring one.

### Step 3 — Review against the rubric

The script cannot tell whether a description is *good*, only that it exists. Read
the skill in full and score it against
[references/review-rubric.md](references/review-rubric.md), which covers
discoverability, instruction quality, information architecture, script hygiene,
and safety.

Report the two or three highest-impact problems, not every nitpick. A weak
description outranks every formatting issue: a skill that never triggers has no
other qualities.

### Step 4 — Trigger test

Discovery is the failure mode nobody tests. From the description alone, write
three requests a user would plausibly make:

1. one the skill **must** trigger on;
2. one adjacent request it **must not** trigger on;
3. one ambiguous request that could match a neighbouring skill.

Read the description as Claude would see it and decide whether it separates the
three. If it does not, rewrite the description — that is the fix.

### Step 5 — Report

Give the user:

- **Verdict**: ready to merge, or blocked.
- **Errors**: what was fixed, and what still needs a decision.
- **Top improvements**: two or three, each with the concrete rewrite, not just
  the diagnosis.
- **Trigger test**: the three requests and the verdict on each.

Suggest rewrites as text the author can paste. Do not rewrite a whole SKILL.md
unasked.

## Scripts

| Script | Purpose |
|:-------|:--------|
| `scripts/validate_skills.py` | The mechanical checks. Run it; do not reimplement its rules by hand. |

Exit codes: `0` clean, `1` errors found (or warnings with `--strict`), `2` bad
usage. CI runs it on every pull request.

## Guardrails

- Never mark a skill ready while the validator reports errors.
- Never weaken a rule to make the validator pass — fix the skill instead.
- Never edit a skill outside the scope the user asked for; report the rest.
- When a warning is genuinely wrong for a skill, say so explicitly in the report
  rather than silently ignoring it.
