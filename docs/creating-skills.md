# Creating a skill

## Ask Claude Code

The `somnio-skill-creator` skill runs the whole flow, starting with the questions
that decide whether the skill will ever be discovered:

```
Create a skill that <what it should do>
```

It frames the job, checks the skill does not already exist, confirms this
repository is the right home, scaffolds the folder, wires the plugin symlink, and
syncs the README index.

## Or drive the scaffolder directly

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --description "What it does. Use this skill when ..."
```

It refuses names that are not kebab-case, exceed 64 characters, or contain the
reserved words Anthropic's spec forbids.

Creating a skill for another area? The same scaffolder targets any repository:

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --repo-root ../somnio-finance-ai --description "..."
```

## Does it belong here?

This repository holds only skills **every area** could use. Everything else
belongs to its area:

| If the skill serves | It belongs in |
|:--------------------|:--------------|
| Every area | `somnio-ai-solutions` |
| Engineering / QA only | `somnio-engineering-ai` |
| Finance only | `somnio-finance-ai` |
| Pre-sales only | `somnio-pre-sales-ai` |

## Then write it

The full standard is
[authoring-standard.md](../skills/somnio-skill-creator/references/authoring-standard.md).
The short version:

1. **The `description` is the product.** It is the only text Claude reads when
   deciding whether to load the skill. Third person, what it does *and* when to
   use it, the words a user would really type, and at least one explicit
   non-trigger naming the neighbouring skill.
2. **Assume Claude is smart.** Only write what it does not already know.
3. **Under 500 lines.** Longer material goes to `references/`, one level deep and
   linked from `SKILL.md`.
4. **Scripts over prose for deterministic work**, and say plainly whether Claude
   should run the script or read it.
5. **Delete the template's authoring notes** — the validator rejects them, on
   purpose.

## Verify before the pull request

```bash
python3 skills/somnio-skill-verifier/scripts/validate_skills.py skills/<skill-name>
make check
```

Then run the `somnio-skill-verifier` skill for the qualitative pass: the script
can tell that a description exists, not that it is any good.
