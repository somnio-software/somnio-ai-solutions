---
name: {{SKILL_NAME}}
description: >
  {{SKILL_DESCRIPTION}}
  Use this skill when the user asks to <trigger 1>, <trigger 2>, or mentions
  <keyword>. Do not use it for <explicit non-trigger>.
---

# {{SKILL_TITLE}}

<!--
  Authoring notes (delete this comment before committing):
  - `name` must match the folder name exactly (kebab-case, <= 64 chars).
  - `description` is the ONLY thing Claude reads when deciding to load the skill.
    Write it in third person, state WHAT it does and WHEN to use it, and include
    the words a user would realistically type.
  - Keep this file under ~500 lines. Push long material into `references/`
    and executable steps into `scripts/`.
  - See ../../docs/skill-conventions.md for the full checklist.
-->

## Purpose

One paragraph: what this skill produces and for whom.

## When to use

- Use when ...
- Use when ...
- Do **not** use when ...

## Inputs

| Input | Required | Notes |
|:------|:---------|:------|
| ... | Yes | ... |

## Workflow

### 1. Collect the inputs

Ask for anything missing with `AskUserQuestion`, one question at a time.

### 2. Do the work

Describe the concrete steps. Prefer imperative instructions over prose.

### 3. Deliver the output

State exactly what the user receives and where it is written.

## Output

Describe the format (markdown report, `.docx`, JSON, files on disk, ...).

## Guardrails

- Never invent data that was not provided or verified.
- Ask before overwriting existing files.
- Report what was skipped and why.

## Resources

- `scripts/` — executable helpers invoked by this skill.
- `references/` — long-form material loaded on demand, not upfront.
