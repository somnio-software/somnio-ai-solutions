<div align="center">

# Somnio AI Solutions

**Somnio Software's repository of generic, cross-area Claude Code skills.**

The skills that every area shares — including the ones that create and verify all the other Somnio skills.

[![Status: Internal](https://img.shields.io/badge/Status-Internal%20Only-red?style=for-the-badge)](#)
[![Scope: Cross-area](https://img.shields.io/badge/Scope-Cross--area-purple?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

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
| 📈 **Sales** | [`somnio-sales-ai`](https://github.com/somnio-software/somnio-sales-ai) | Sales skills — pipeline, deals, and client follow-up |
| 📣 **Marketing** | [`somnio-marketing-ai`](https://github.com/somnio-software/somnio-marketing-ai) | Marketing skills — content, campaigns, and brand material |
| 🧑‍🤝‍🧑 **HR** | [`somnio-hr-ai`](https://github.com/somnio-software/somnio-hr-ai) | HR skills — hiring, onboarding, and people operations |

> **Rule of thumb:** if a skill only makes sense for one area, it belongs in that area's repository. If any area could use it, it belongs here.

---

## 📚 Documentation

Full documentation lives in [`docs/`](./docs).

| Page | What it covers |
|:-----|:---------------|
| [Installation](./docs/installation.md) | Installing the plugin in Claude Code and in Claude Desktop (Cowork) |
| [Repository structure](./docs/repository-structure.md) | The tree, the `skills/` ↔ `plugins/` symlink contract, the Makefile |
| [Creating a skill](./docs/creating-skills.md) | Scaffolding a skill and writing it to the standard |
| [Importing a skill](./docs/importing-skills.md) | Adopting a skill copied from another repository with the `skill-importer` agent |
| [Testing](./docs/testing.md) | The suite, the 100% per-file coverage gate, and the pre-push hook |
| [Pipeline](./docs/pipeline.md) | What CI validates and how the plugin archive is built and committed |
| [Contributing](./docs/contributing.md) | Branch, review and merge workflow |

The two documents that outrank everything else live inside the skills, so they travel with them to the other `somnio-*-ai` repositories: the [authoring standard](./skills/somnio-skill-creator/references/authoring-standard.md) and the [review rubric](./skills/somnio-skill-verifier/references/review-rubric.md).

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

**The harness is made of skills.** There is no separate tooling directory: `somnio-skill-creator` scaffolds and wires new skills, `somnio-skill-verifier` validates them, and the [`skill-importer`](./.claude/agents/skill-importer.md) agent drives both to adopt skills copied from elsewhere. All of them work against any Somnio repository via `--repo-root`, which is how the standard stays identical across areas.

---

## 🚀 Quick Start

```bash
make help          # list every target
make hooks         # enable the versioned pre-push hook (once per clone)
make check         # what CI checks on a pull request
```

Install the plugin — see [Installation](./docs/installation.md) — then ask Claude Code for a skill by name. Each skill's `SKILL.md` contains its full usage instructions, required inputs, and expected outputs.

To add a skill, ask Claude Code to create one ([Creating a skill](./docs/creating-skills.md)) or hand it an existing one to adopt ([Importing a skill](./docs/importing-skills.md)). Never create the folder by hand.

---

## 🤝 Contributing

Branch from `main`, follow [`CLAUDE.md`](./CLAUDE.md) and the [authoring standard](./skills/somnio-skill-creator/references/authoring-standard.md), make `make check` pass, and open a pull request. The full workflow and what reviewers block on is in [Contributing](./docs/contributing.md).

---

## 🔒 Repository Status

Internal Somnio Software repository. **Not for distribution outside the organization.**

Licensed under the [MIT License](./LICENSE) — the same terms the rest of Somnio's AI repositories carry, so code can move between them and be opened up later without a relicensing exercise.
