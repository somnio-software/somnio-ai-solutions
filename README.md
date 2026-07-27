<div align="center">

# Somnio AI Solutions

**Somnio Software's repository of generic, cross-area Claude Code skills.**

The skills that every area shares — including the ones that create and verify all the other Somnio skills.

[![Status: Internal](https://img.shields.io/badge/Status-Internal%20Only-red?style=for-the-badge)](#)
[![Scope: Cross-area](https://img.shields.io/badge/Scope-Cross--area-purple?style=for-the-badge)](#)

[![Claude Code](https://img.shields.io/badge/Claude%20Code-D97757?style=flat-square&logo=anthropic&logoColor=white)](#)
[![Skills](https://img.shields.io/badge/Skills-SKILL.md-3178C6?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](#)

</div>

---

## 🧭 Somnio AI Repositories

Every area owns its own repository of Claude Code skills. This one holds what is **not** tied to any single area.

| Area | Repository | What lives there |
|:-----|:-----------|:-----------------|
| 🌐 **Cross-area** | [`somnio-ai-solutions`](https://github.com/somnio-software/somnio-ai-solutions) **(this repo)** | Generic skills usable by every area — skill creation, verification, and the shared authoring standard |
| ⚙️ **Engineering** | [`somnio-engineering-ai`](https://github.com/somnio-software/somnio-engineering-ai) | Engineering & QA management skills — HandShake pipeline, job descriptions, AI usage reports, seniority evaluation |
| 💰 **Finance** | [`somnio-finance-ai`](https://github.com/somnio-software/somnio-finance-ai) | Finance skills — billing, reporting, and financial operations |
| 🤝 **Pre-Sales** | [`somnio-pre-sales-ai`](https://github.com/somnio-software/somnio-pre-sales-ai) | Pre-sales skills — proposals, estimations, and client-facing material |

> **Rule of thumb:** if a skill only makes sense for one area, it belongs in that area's repository. If any area could use it, it belongs here.

---

## 🎯 Purpose

Centralize in a single repository the skills that are **area-agnostic**:

- 🧱 **Meta-skills** that create and verify other Somnio skills, so every area repository stays consistent.
- 📐 **One authoring standard**, based on Anthropic's Agent Skills spec and best practices, shared by all four repositories.
- ♻️ **Reusable workflows** any area can install without inheriting another area's tooling.
- 🤖 **A pipeline** that validates every change and rebuilds the plugin archive on merge.

> Every skill here is built for **internal Somnio use**. None of these are customer-facing products.

---

## 🛠️ Skills

Reusable Claude Code skills. Each one is a standalone folder with a `SKILL.md` and optional `scripts/`, `references/` and `assets/`.

> This table is generated from each `SKILL.md` frontmatter — run `make sync` instead of editing it by hand.

<!-- skills:start -->

| Skill | Description |
|:------|:------------|
| [`somnio-skill-creator`](./skills/somnio-skill-creator) | Creates a new Claude Code skill in a Somnio repository — scaffolds the folder, writes SKILL.md to Anthropic's spec, wires the plugin symlink, and updates the README index. |
| [`somnio-skill-verifier`](./skills/somnio-skill-verifier) | Reviews existing Claude Code skills against Anthropic's spec and Somnio's standard, then reports what to fix — frontmatter limits, description quality, progressive disclosure, script hygiene, and plugin symlinks. |

<!-- skills:end -->

**The harness is made of skills.** There is no separate tooling directory: `somnio-skill-creator` scaffolds and wires new skills, `somnio-skill-verifier` validates them. Both work against any Somnio repository via `--repo-root`, which is how the standard stays identical across areas.

The authoring standard itself lives in [`references/authoring-standard.md`](./skills/somnio-skill-creator/references/authoring-standard.md) — the single source of truth for all four repositories.

---

## 🔌 Plugin

All skills ship as a single plugin, [`plugins/somnio-ai-solutions/`](./plugins/somnio-ai-solutions):

```
plugins/somnio-ai-solutions/
├── .claude-plugin/plugin.json        # Plugin manifest
└── skills/
    ├── somnio-skill-creator          # symlink -> ../../../skills/somnio-skill-creator
    └── somnio-skill-verifier         # symlink -> ../../../skills/somnio-skill-verifier
```

Skill entries are **symlinks**, never copies, so the plugin can never drift from the source of truth in `skills/`.

### Install in Claude Code (recommended)

The repository root is a Claude Code marketplace ([`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json)):

```bash
/plugin marketplace add somnio-software/somnio-ai-solutions
/plugin install somnio-ai-solutions@somnio-ai
```

Working on the repo locally? Point the marketplace at your clone instead:

```bash
/plugin marketplace add ./
/plugin install somnio-ai-solutions@somnio-ai
/reload-plugins
```

### Install in Claude Desktop (Cowork)

Claude Desktop requires a `.zip`, and **CI builds it for you** — download the committed `plugins/somnio-ai-solutions.zip` from `main`, then:

1. Open **Claude Desktop** → **Cowork** tab
2. Click **Customize** in the left sidebar
3. Click **Browse plugins**
4. Select **Upload a custom plugin file** and choose the `.zip`

The plugin is saved locally to your machine. Repeat whenever the archive is updated on `main`.

---

## 🤖 Pipeline

[`.github/workflows/skills.yml`](./.github/workflows/skills.yml) owns everything mechanical.

| Trigger | What runs |
|:--------|:----------|
| Pull request touching `skills/` or `plugins/` | Validates every skill and fails if the README table is stale |
| Push to `main` touching `skills/` or `plugins/` | Repairs symlinks, syncs the README, rebuilds `plugins/somnio-ai-solutions.zip`, verifies it is self-contained, and commits it back |

The archive is committed by the pipeline, so **never commit a locally built `.zip`**. Timestamps are normalized before zipping, so a run with no real change produces no commit.

---

## 🗂️ Structure

```
somnio-ai-solutions/
├── CLAUDE.md                                 # Repo-wide rules for Claude Code
├── Makefile                                  # Thin entry points to the skills' scripts
├── README.md                                 # This file
├── .claude-plugin/
│   └── marketplace.json                      # Makes this repo a Claude Code marketplace
├── .github/workflows/skills.yml              # Validate on PR · package + commit on main
├── skills/                                   # Source of truth — one folder per skill
│   ├── somnio-skill-creator/
│   │   ├── SKILL.md
│   │   ├── scripts/                          # scaffold_skill.py · sync_readme.py
│   │   ├── references/                       # authoring-standard.md · repository-layout.md
│   │   └── assets/skill-template/            # The scaffold every new skill starts from
│   └── somnio-skill-verifier/
│       ├── SKILL.md
│       ├── scripts/validate_skills.py        # The mechanical checks CI runs
│       └── references/review-rubric.md       # What to judge once the script is clean
└── plugins/
    └── somnio-ai-solutions/                  # Plugin manifest + symlinks to skills/
```

Skills have **no runtime dependencies** — they are plain folders consumed by Claude Code. Their scripts use the system `python3`, stdlib only.

---

## ➕ Adding a New Skill

Ask Claude Code — the creator skill runs the whole flow, including the questions that make a skill discoverable:

```
Create a skill that <what it should do>
```

Under the hood it scaffolds from the template, symlinks the plugin, and syncs this README. To drive it directly:

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --description "What it does. Use this skill when ..."
```

Then write the skill, and verify before opening the pull request:

```bash
make check      # validate every skill + confirm the README table is in sync
```

Creating a skill for another area? The same scaffolder targets any repository:

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --repo-root ../somnio-finance-ai --description "..."
```

---

## 🚀 Quick Start

```bash
make help          # list every target
make validate      # frontmatter, naming, references and plugin symlinks
make fix           # recreate missing plugin symlinks, drop orphans
make sync          # regenerate the Skills table in this README
make check         # what CI checks on a pull request
make zip           # build the archive locally (CI does it on merge)
```

Skills are invoked from Claude Code or Claude Cowork once the plugin is installed. Each skill's `SKILL.md` contains its full usage instructions, required inputs, and expected outputs.

---

## 🤝 Contributing

Internal contribution workflow:

1. Create a feature branch from `main`.
2. Follow [`CLAUDE.md`](./CLAUDE.md) and the [authoring standard](./skills/somnio-skill-creator/references/authoring-standard.md).
3. Run the `somnio-skill-verifier` skill on what you changed, and make `make check` pass.
4. Open a pull request and request review from the relevant team.

---

## 🔒 Repository Status

Internal Somnio Software repository. **Not for distribution outside the organization.**
