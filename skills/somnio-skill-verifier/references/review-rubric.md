# Skill Review Rubric

What to judge once the validator is clean. Five dimensions, ordered by impact.
Score each: **blocking**, **should fix**, or **fine**.

## Contents

- 1. Discoverability
- 2. Instruction quality
- 3. Information architecture
- 4. Script hygiene
- 5. Safety and honesty
- Severity guide
- Report format

---

## 1. Discoverability

The highest-impact dimension. A skill that never triggers has no other qualities.

- Does the description state **what it does** and **when to use it**?
- Is it **third person**? "I can help you ..." and "You can use this to ..." both
  degrade discovery.
- Does it contain the **words a user would really type** — formats, tool names,
  process names, and the Spanish terms if the team is bilingual?
- Does it name at least one **non-trigger** when a neighbouring skill exists?
- Would it collide with another installed skill? Two descriptions matching the
  same request means one of them must narrow.

**Blocking** when the description is generic ("Helps with documents"), first
person, or indistinguishable from another skill.

---

## 2. Instruction quality

- Is the workflow a **sequence of steps** with clear entry and exit conditions,
  rather than prose to interpret?
- Does the level of specificity match the fragility of the task? Exact commands
  where consistency is critical; direction where judgement applies.
- Are the **inputs** stated, along with what to do when one is missing?
- Is there a **verification step** for anything destructive, batched, or
  externally visible, with a loop back on failure?
- Are examples **concrete**? Abstract placeholders teach nothing.
- Is one term used per concept throughout?
- Does it explain things Claude already knows? Cut them.

**Blocking** when a critical operation has no verification, or when the steps are
ambiguous enough that two runs would diverge.

---

## 3. Information architecture

- Is the `SKILL.md` body under 500 lines, and is what remains genuinely needed
  every time the skill triggers?
- Is every reference file **linked from `SKILL.md`** and **one level deep**? A
  reference that links onward to another file may only be read partially.
- Do reference files over 100 lines open with a `## Contents` list?
- Are file names descriptive of their content?
- Is bundled material actually used? An unreferenced file is dead weight.

**Should fix** in most cases; **blocking** when a reference is unreachable or a
nested chain hides required information.

---

## 4. Script hygiene

- Does the skill say whether to **run** the script or **read** it?
- Do the scripts **handle their own errors** instead of failing and leaving
  Claude to improvise?
- Are constants justified in comments — no unexplained timeouts or retry counts?
- Are error messages specific enough to act on ("Field 'x' not found. Available:
  a, b, c")?
- Are dependencies either stdlib-only or declared explicitly?
- Are all paths forward-slashed?

**Blocking** when a script fails silently or a dependency is assumed without
being declared.

---

## 5. Safety and honesty

- Does the skill state what it must **never** invent or fabricate?
- Does it ask before overwriting files or performing outward-facing actions?
- Does it require reporting what was skipped and why?
- Does it avoid fetching and executing content from untrusted external sources?
- For MCP tools, are names fully qualified (`ServerName:tool_name`)?

**Blocking** when a skill can produce plausible fabricated output — a report, a
record, an evaluation — with no instruction to ground it in real inputs.

---

## Severity guide

| Severity | Meaning |
|:---------|:--------|
| **Blocking** | Do not merge. The skill will not trigger, will diverge between runs, or can produce fabricated or destructive output. |
| **Should fix** | Merge is acceptable, but it will cost tokens, clarity, or maintenance. |
| **Fine** | Style preference. Mention at most in passing. |

---

## Report format

```markdown
**Verdict:** ready to merge | blocked

**Errors fixed:** ...
**Still open:** ...

**Top improvements**
1. [dimension] problem — concrete rewrite
2. ...

**Trigger test**
- Must trigger: "..." → yes/no
- Must not trigger: "..." → yes/no
- Ambiguous: "..." → resolved by ...
```

Two or three improvements, each with the replacement text. A list of twenty
nitpicks gets ignored; three concrete rewrites get applied.
