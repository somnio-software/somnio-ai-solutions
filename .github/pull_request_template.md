## What

<!-- One line: which skill was added or changed, and why. -->

## Checklist

- [ ] `make check` passes locally (validation, README sync, tests at 100% per-file coverage)
- [ ] New or changed script lines are covered by a test — the gate never goes down
- [ ] Reviewed with the `somnio-skill-verifier` skill, and its blocking findings are resolved
- [ ] The skill is **cross-area** (area-specific skills belong in that area's repo)
- [ ] Frontmatter `description` names concrete triggers and at least one non-trigger
- [ ] Authoring notes removed from `SKILL.md`
- [ ] Tried end-to-end in a fresh Claude Code session
- [ ] `plugin.json` `version` bumped if the set of skills changed
- [ ] No locally built `.zip` committed — CI rebuilds it on merge
