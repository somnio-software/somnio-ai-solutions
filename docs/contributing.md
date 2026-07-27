# Contributing

Internal workflow. Everything here is for Somnio use only — see
[Repository status](../README.md#-repository-status).

## Before your first change

```bash
make hooks       # enable the versioned pre-push hook
make check       # confirm the repository is green on your machine
```

## The loop

1. **Branch from `main`.**
2. **Create or import the skill** with the tooling, never by hand —
   [Creating a skill](creating-skills.md) or [Importing a skill](importing-skills.md).
3. **Write it** against the
   [authoring standard](../skills/somnio-skill-creator/references/authoring-standard.md),
   and any script against the [Python rules](../.claude/rules).
4. **Review it** with the `somnio-skill-verifier` skill and resolve every
   blocking finding from the
   [rubric](../skills/somnio-skill-verifier/references/review-rubric.md).
5. **Run `make check`.** It is what CI and the hook run.
6. **Open a pull request** and request review from the relevant team. The
   [template](../.github/pull_request_template.md) carries the checklist.

## What reviewers block on

- A description that would not trigger, or that collides with an existing skill.
- A skill that is area-specific and belongs in `somnio-engineering-ai`,
  `somnio-finance-ai` or `somnio-pre-sales-ai`.
- Template authoring notes left in `SKILL.md`.
- A script with a third-party import, or with no test covering its lines.
- A hand-edited README skills table, or a hand-made plugin symlink.
- A locally built `.zip` in the diff.
- A lowered coverage threshold or a weakened validator rule.

## Conventions

- **Everything in the repository is written in English** — see
  [`CLAUDE.md`](../CLAUDE.md). The exception is content that exists as an
  explicit translation, where each file is written in its own language.
- Commit messages follow Conventional Commits.
- Bump `version` in the plugin manifest when the set of skills changes.
