# Importing a skill

Copied a skill from another repository, a plugin or a teammate? Hand it to the
[`skill-importer`](../.claude/agents/skill-importer.md) agent instead of adapting
it by hand.

```
Use the skill-importer agent
https://github.com/somnio-software/somnio-ai-tools/blob/main/skills/<name>/SKILL.md
```

## It waits for the source

The agent asks for the URL or path and **stops until it gets one**. It never
scans `skills/` for untracked folders and never picks the obvious candidate — a
wrong guess rewrites the wrong skill. It accepts:

- a local path — `skills/foo`, `../other-repo/skills/foo`, `~/Downloads/foo/SKILL.md`;
- a GitHub `blob`, `tree` or `raw` URL;
- a git remote plus the path inside it.

A lone `SKILL.md` is fetched raw. A skill with `references/`, `scripts/` or
`assets/` is cloned, over SSH when the repository is private — HTTPS without a
token and an unauthenticated `gh` both fail against Somnio's private repos.

## What it does

1. Confirms the skill is genuinely cross-area, and redirects it to its area's
   repository when it is not.
2. Strips the foreign material — `.git/`, lockfiles, CI config, the origin's own
   README — and asks before deleting anything it cannot classify.
3. Normalizes the folder name and frontmatter `name` to the spec.
4. Rewrites the description for *this* skill library, then runs the trigger test
   from the rubric.
5. Rewrites the body to the standard: English, under 500 lines, references one
   level deep, forward slashes, no time-sensitive statements.
6. Audits any bundled script against the [Python rules](../.claude/rules) and
   flags a third-party import as blocking.
7. Warns that an imported script needs tests, because the
   [coverage gate](testing.md) is 100% per file for the whole repository.
8. Wires the plugin symlink, syncs the README, and loops on the validator until
   it is clean.

It reports what it renamed, deleted and rewrote, the trigger test, the real gate
output, and every decision it refused to take alone.

## It uses this repository's skills

The agent drives `somnio-skill-creator` and `somnio-skill-verifier` and runs
`validate_skills.py` — it does not reimplement the checks. That is what keeps an
imported skill indistinguishable from one written here.
