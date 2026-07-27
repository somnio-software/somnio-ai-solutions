<div align="center">

# Somnio AI Solutions

**Somnio Software's repository of generic, cross-area Claude Code skills.**

The skills that every area shares — authoring, verifying, and standardizing the rest of Somnio's AI tooling.

[![Status: Internal](https://img.shields.io/badge/Status-Internal%20Only-red?style=for-the-badge)](#)
[![Scope: Cross-area](https://img.shields.io/badge/Scope-Cross--area-purple?style=for-the-badge)](#)

[![Claude Code](https://img.shields.io/badge/Claude%20Code-D97757?style=flat-square&logo=anthropic&logoColor=white)](#)
[![Skills](https://img.shields.io/badge/Skills-SKILL.md-3178C6?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![Make](https://img.shields.io/badge/Make-427819?style=flat-square&logo=gnu&logoColor=white)](#)

</div>

---

## 🧭 Somnio AI Repositories

Every area owns its own repository of Claude Code skills. This one holds what is **not** tied to any single area.

| Area | Repository | What lives there |
|:-----|:-----------|:-----------------|
| 🌐 **Cross-area** | [`somnio-ai-solutions`](https://github.com/somnio-software/somnio-ai-solutions) **(this repo)** | Generic skills usable by every area — skill creation, verification, and shared conventions |
| ⚙️ **Engineering** | [`somnio-engineering-ai`](https://github.com/somnio-software/somnio-engineering-ai) | Engineering & QA management skills — HandShake pipeline, job descriptions, AI usage reports, seniority evaluation |
| 💰 **Finance** | [`somnio-finance-ai`](https://github.com/somnio-software/somnio-finance-ai) | Finance skills — billing, reporting, and financial operations |
| 🤝 **Pre-Sales** | [`somnio-pre-sales-ai`](https://github.com/somnio-software/somnio-pre-sales-ai) | Pre-sales skills — proposals, estimations, and client-facing material |

> **Rule of thumb:** if a skill only makes sense for one area, it belongs in that area's repository. If any area could use it, it belongs here.

---

## 🎯 Purpose

Centralize in a single repository the skills that are **area-agnostic**:

- 🧱 **Meta-skills** that create, review, and verify other Somnio skills so every repo stays consistent.
- 📐 **Shared conventions** — one authoring standard, one validator, one review checklist.
- ♻️ **Reusable workflows** that any area can install without inheriting another area's tooling.
- 🚀 **A harness** that makes adding a new skill a one-command operation.

> Every skill here is built for **internal Somnio use**. None of these are customer-facing products.

---

## 🛠️ Skills

Reusable Claude Code skills. Each one is a standalone folder with a `SKILL.md` and optional `scripts/` and `references/`.

> This table is generated from each `SKILL.md` frontmatter — run `make sync` instead of editing it by hand.

<!-- skills:start -->

_No skills yet._ Create the first one with `make new-skill NAME=<skill-name>`.

<!-- skills:end -->

---

## 🔌 Plugin

All skills in this repo ship as a single plugin, [`plugins/somnio-ai-solutions/`](./plugins/somnio-ai-solutions). Skill entries inside the plugin are symlinks pointing to `skills/`, so the plugin is always in sync with the source of truth.

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

Claude Desktop requires plugins to be packaged as a `.zip` archive before uploading:

```bash
make package        # builds plugins/somnio-ai-solutions.zip
```

Then:

1. Open **Claude Desktop** → **Cowork** tab
2. Click **Customize** in the left sidebar
3. Click **Browse plugins**
4. Select **Upload a custom plugin file** and choose the `.zip`

The plugin is saved locally to your machine. Repeat these steps whenever the plugin is updated.

---

## 🗂️ Structure

```
somnio-ai-solutions/
├── CLAUDE.md                             # Repo-wide rules for Claude Code
├── Makefile                              # Harness entry point (make help)
├── README.md                             # This file
├── .claude-plugin/
│   └── marketplace.json                  # Makes this repo a Claude Code marketplace
├── docs/
│   └── skill-conventions.md              # Authoring standard every skill follows
├── skills/                               # Source of truth — one folder per skill
│   └── <skill-name>/
│       ├── SKILL.md                      # Frontmatter + instructions
│       ├── scripts/                      # Executable helpers (optional)
│       └── references/                   # Long-form material, loaded on demand (optional)
├── plugins/
│   └── somnio-ai-solutions/
│       ├── .claude-plugin/plugin.json    # Plugin manifest
│       └── skills/<skill-name>           # Symlink -> ../../../skills/<skill-name>
├── templates/
│   └── skill/                            # Scaffold copied by `make new-skill`
└── scripts/
    ├── new-skill.sh                      # Scaffold + symlink + README sync
    ├── validate-skills.py                # Frontmatter, naming and symlink checks
    ├── sync-readme.py                    # Regenerates the Skills table above
    ├── package-plugin.sh                 # Builds the Cowork .zip
    └── skill_index.py                    # Shared parsing helpers (stdlib only)
```

Skills have **no runtime dependencies** — they are plain folders consumed by Claude Code. The harness only needs `make`, `bash`, `python3`, and `zip`, all of which ship with macOS and Linux.

---

## ➕ Adding a New Skill

One command scaffolds the folder, wires the plugin symlink, and updates this README:

```bash
make new-skill NAME=somnio-skill-creator DESC="Creates new Somnio Claude Code skills from a short brief."
```

Then:

1. **Write the frontmatter `description`.** It is the only thing Claude reads when deciding whether to load the skill — say *what* it does and *when* to use it, in third person, using the words a user would actually type.
2. **Fill in the workflow** in `skills/<skill-name>/SKILL.md` and delete the authoring notes. Keep it under ~500 lines; long material goes in `references/`.
3. **Add helpers** under `scripts/` if the skill needs deterministic steps.
4. **Verify:**

   ```bash
   make check      # validate + confirm the README table is in sync
   ```

5. **Open a pull request.** CI runs the same `make check`.

The full authoring standard lives in [`docs/skill-conventions.md`](./docs/skill-conventions.md).

---

## 🚀 Quick Start

```bash
make help          # list every target
make list          # list the skills in this repo
make validate      # check frontmatter, naming and plugin symlinks
make sync          # regenerate the Skills table in this README
make check         # what CI runs
make package       # build the Cowork .zip
```

Skills are invoked from Claude Code or Claude Cowork once the plugin is installed. Each skill's `SKILL.md` contains its full usage instructions, required inputs, and expected outputs.

---

## 🤝 Contributing

Internal contribution workflow:

1. Create a feature branch from `main`.
2. Follow the conventions in [`CLAUDE.md`](./CLAUDE.md) and [`docs/skill-conventions.md`](./docs/skill-conventions.md).
3. Ensure `make check` passes locally.
4. Open a pull request and request review from the relevant team.

---

## 🔒 Repository Status

Internal Somnio Software repository. **Not for distribution outside the organization.**
