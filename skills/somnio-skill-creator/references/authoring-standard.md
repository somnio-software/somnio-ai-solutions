# Somnio Skill Authoring Standard

The rules every Somnio skill follows. Based on Anthropic's Agent Skills
specification and authoring best practices (`platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`),
plus the conventions shared across the `somnio-*-ai` repositories.

## Contents

- The specification (hard limits)
- Language
- Naming
- Writing the description
- Degrees of freedom
- Progressive disclosure
- Writing scripts
- Anti-patterns
- Evaluating a skill
- Release checklist

---

## The specification (hard limits)

Every skill is a folder containing a `SKILL.md` whose YAML frontmatter has two
required fields:

```yaml
---
name: billing-report
description: Generates the monthly billing report from Clockify exports. Use when ...
---
```

`name`

- Maximum 64 characters.
- Lowercase letters, numbers and hyphens only.
- No XML tags.
- Cannot contain the reserved words "anthropic" or "claude".
- Must match the folder name exactly.

`description`

- Non-empty, maximum 1024 characters.
- No XML tags.
- Must state both what the skill does and when to use it.

Optional fields Claude Code understands: `allowed-tools` (restricts the tools the
skill may use), `license`, `metadata`.

Everything else is convention, not schema — but the conventions below are what
make a skill actually get used.

---

## Language

Every Somnio skills repository is written in **English** — the description, the
body, references, script comments, error strings and file names. One language
across four repositories is what lets a skill move between them, and what lets
anyone review any skill.

Two exceptions, and no others:

- **Trigger vocabulary.** A description names the words a user would really type,
  and a bilingual team types some of them in Spanish. Quote them:
  `including the Spanish phrasings "crear una skill", "revisar la skill"`. That is
  vocabulary inside an English sentence, not Spanish prose.
- **Explicit translations.** When the same material must exist in several
  languages — form labels, question banks, anything the skill hands to a person —
  each translation is its own file, written in its own language and **named for
  it**: `references/labels/en.md` and `references/labels/es.md`, or
  `references/questions-en/` and `references/questions-es/`. English is the source
  the others follow, and the instructions around them stay in English.

The validator flags prose that reads as Spanish in `SKILL.md` and in `references/`,
skipping files named for a language. It is a warning, not an error, because the
heuristic cannot be perfect — treat it as one.

When a skill has to be translated to meet this, the translation changes the
language and nothing else: same steps, same order, same commands, same
thresholds, same outputs.

---

## Naming

Prefer gerunds or clear noun phrases that say what the skill *does*:
`generating-invoices`, `billing-report`, `qa-seniority-check`.

Avoid `helper`, `utils`, `tools`, `data`, `files` — they are invisible in a list
of a hundred skills.

Somnio adds one convention: prefix with `somnio-` only when the skill acts on
Somnio's own tooling or process (`somnio-skill-creator`,
`somnio-skill-verifier`). Domain skills do not carry the prefix.

Stay consistent inside a repository. Mixed naming patterns make skills hard to
discuss and hard to find.

---

## Writing the description

At startup Claude loads only the `name` and `description` of every installed
skill — roughly 100 tokens each. That metadata is the entire basis for choosing
this skill over the other hundred. The body is never consulted for that decision.

**Always third person.** The description is injected into the system prompt;
first or second person causes discovery problems.

- Good: "Generates the monthly billing report ..."
- Avoid: "I can help you generate ..." / "You can use this to generate ..."

**Include the trigger vocabulary.** Real words a user types: file formats
(`.xlsx`, `.docx`), tool names (Clockify, Jira), process names (HandShake), and
the Spanish terms too when the team works bilingually.

**Include a non-trigger** whenever a neighbouring skill exists. It is what stops
two skills from fighting over the same request.

Effective:

```yaml
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Useless:

```yaml
description: Helps with documents
```

---

## Degrees of freedom

Match specificity to how fragile the task is.

| Freedom | Use when | Form |
|:--------|:---------|:-----|
| High | Many valid approaches, context decides | Prose steps and heuristics |
| Medium | A preferred pattern with acceptable variation | Pseudocode, parameterised script |
| Low | Fragile, consistency is critical, exact sequence | One exact command, "do not add flags" |

Think of it as a path: an open field needs a direction, a narrow bridge needs
guardrails. Over-constraining an open field wastes tokens; under-constraining a
bridge produces broken output.

---

## Progressive disclosure

Content loads in three levels: metadata always, `SKILL.md` when the skill
triggers, bundled files only when read. Structure for that.

- Keep the `SKILL.md` body **under 500 lines**. Split before you approach it.
- `SKILL.md` is a table of contents that points to detail, not the detail itself.
- **Keep references one level deep.** A file referenced from a referenced file
  may only be read partially, so every reference links directly from `SKILL.md`.
- Organise reference files by domain (`references/finance.md`,
  `references/sales.md`), so a task loads only what it needs.
- Any reference file over 100 lines opens with a `## Contents` list, so a partial
  read still reveals the full scope.
- Name files by content: `form_validation_rules.md`, never `doc2.md`.

---

## Writing scripts

Scripts are executed through bash and their source never enters the context
window — only their output. That makes them cheaper *and* more reliable than
having Claude regenerate equivalent code.

- **Solve, don't defer.** Handle the error inside the script instead of failing
  and leaving Claude to improvise.
- **No voodoo constants.** Justify every timeout, retry count and threshold in a
  comment. If you cannot, Claude certainly cannot.
- **Say run or read.** "Run `validate.py` to check the mapping" (execute) versus
  "See `validate.py` for the algorithm" (read). Execution is the default.
- **Stdlib only, or declare dependencies.** Somnio harness scripts run with the
  system `python3` and no packages. If a skill truly needs third-party libraries,
  ship a `requirements.txt` inside the skill folder and document the setup.
- **Emit verbose, specific errors.** "Field 'signature_date' not found. Available:
  customer_name, order_total" beats "invalid field".
- **Build feedback loops.** Run validator, fix, repeat until clean, then proceed.
  For batch or destructive work, have Claude write a plan file, validate the
  plan, then execute it.

---

## Anti-patterns

- Windows-style paths — always forward slashes, on every platform.
- A menu of options ("use pypdf, or pdfplumber, or PyMuPDF") — give one default
  plus an escape hatch.
- Time-sensitive instructions ("before August, use the old API") — put superseded
  behaviour in an "old patterns" section.
- Inconsistent terminology — one term per concept, all the way through.
- Explaining what Claude already knows — it costs context and adds nothing.
- Unqualified MCP tool names — write `ServerName:tool_name`.
- Assuming a package is installed without saying so.

---

## Evaluating a skill

Build the evaluation before writing the documentation, so the skill solves a real
gap rather than an imagined one:

1. Run the task with no skill and record exactly where Claude fails.
2. Write three representative scenarios that exercise those failures.
3. Write the minimum instructions that make them pass.
4. Test in a fresh session — a skill that works when you explain it in
   conversation proves nothing.
5. Watch how Claude navigates it: files read in an unexpected order, references
   never followed, or a bundled file never opened all point at structure problems.

Test with every model the team uses. Opus tolerates terse instructions that Haiku
needs spelled out.

---

## Release checklist

- [ ] `name` matches the folder, is kebab-case, and holds no reserved word.
- [ ] Description is third person and names both triggers and a non-trigger.
- [ ] Body is under 500 lines, with detail pushed into `references/`.
- [ ] Every reference is linked from `SKILL.md` and is one level deep.
- [ ] Examples are concrete, not abstract.
- [ ] Scripts handle their own errors and document their constants.
- [ ] Critical operations have a verification step and a feedback loop.
- [ ] No time-sensitive information, no Windows paths, no template leftovers.
- [ ] Tried end-to-end in a fresh Claude Code session.
- [ ] The automated validator passes.
