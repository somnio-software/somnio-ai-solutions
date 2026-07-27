---
name: {{SKILL_NAME}}
description: >
  {{SKILL_DESCRIPTION}}
---

# {{SKILL_TITLE}}

<!--
  AUTHORING NOTES — delete this comment before committing.

  1. The description above is the whole product surface. It is the only text
     Claude sees when deciding whether to load this skill. Third person, what it
     does AND when to use it, with the words a user would actually type, plus at
     least one explicit non-trigger.
  2. Assume Claude is smart. Only write what it does not already know.
  3. Keep this body under 500 lines. Long material goes in references/,
     deterministic steps go in scripts/. Delete the folders you do not use.
  4. Validate before committing:
     python3 skills/somnio-skill-verifier/scripts/validate_skills.py
-->

## Purpose

One paragraph: what this skill produces and for whom.

## When to use

- Use when ...
- Use when ...
- Do **not** use when ... (say which skill covers that instead)

## Inputs

| Input | Required | Notes |
|:------|:---------|:------|
| ... | Yes | ... |

Ask for anything missing with `AskUserQuestion`, one question at a time. Never
invent an input that was not provided.

## Workflow

Copy this checklist and tick items off as you go:

```
- [ ] Step 1: Collect the inputs
- [ ] Step 2: Do the work
- [ ] Step 3: Verify the output
```

### Step 1 — Collect the inputs

Describe exactly what to gather and how.

### Step 2 — Do the work

Imperative instructions. Prefer running a script over improvising when the
operation is deterministic.

### Step 3 — Verify the output

State the check that must pass. If it fails, return to Step 2.

## Output

Format, location, and filename of what the user receives.

## Guardrails

- Never invent data that was not provided or verified.
- Ask before overwriting an existing file.
- Report explicitly what was skipped and why.
