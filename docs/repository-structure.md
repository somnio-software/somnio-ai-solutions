# Repository structure

```
somnio-ai-solutions/
├── CLAUDE.md                                 # Repo-wide rules for Claude Code
├── Makefile                                  # Thin entry points to the skills' scripts
├── README.md                                 # Repository index
├── .claude/
│   ├── agents/skill-importer.md              # Adopts a skill copied from another repo
│   └── rules/python/                         # Python rules, adapted from somnio-ai-tools
├── .claude-plugin/
│   └── marketplace.json                      # Makes this repo a Claude Code marketplace
├── .githooks/pre-push                        # Validate · sync · test before every push
├── .github/workflows/skills.yml              # Validate + test on PR · package on main
├── docs/                                     # This documentation
├── tests/                                    # Suite + the 100% per-file coverage gate
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

Skills have **no runtime dependencies** — they are plain folders consumed by
Claude Code. Their scripts use the system `python3`, stdlib only.

## `skills/` is the only source of truth

```
plugins/somnio-ai-solutions/
├── .claude-plugin/plugin.json        # Plugin manifest
└── skills/
    ├── somnio-skill-creator          # symlink -> ../../../skills/somnio-skill-creator
    └── somnio-skill-verifier         # symlink -> ../../../skills/somnio-skill-verifier
```

Plugin entries are **symlinks, never copies**, so the plugin cannot drift from
the skill it publishes, and `zip` dereferences them when packaging so the archive
stays self-contained. A copy is a validation error, not a style preference.

`validate_skills.py --fix` creates a missing symlink and drops one left behind by
a rename — never hand-write them. The full rationale, and the layout every
`somnio-*-ai` repository shares, is in the skill's own reference:
[repository-layout.md](../skills/somnio-skill-creator/references/repository-layout.md).

## The harness is made of skills

There is no tooling directory. The scripts that create and validate skills live
inside the skills that own them, so they travel with the plugin and work against
any Somnio repository through `--repo-root`:

| Script | Owner skill | Job |
|:-------|:------------|:----|
| `scaffold_skill.py` | `somnio-skill-creator` | Create the folder, the plugin symlink and the README row |
| `sync_readme.py` | `somnio-skill-creator` | Regenerate the README skills table between its markers |
| `validate_skills.py` | `somnio-skill-verifier` | The mechanical checks, plus `--fix` for symlinks |

## Makefile

Thin entry points to those scripts — the same commands CI and the pre-push hook
run:

```bash
make help          # list every target
make hooks         # enable the versioned pre-push hook (once per clone)
make validate      # frontmatter, naming, references and plugin symlinks
make fix           # recreate missing plugin symlinks, drop orphans
make sync          # regenerate the Skills table in the README
make test          # run the harness test suite
make coverage      # run it with the 100% per-file gate
make check         # validate + sync-check + coverage
make zip           # build the archive locally (CI does it on merge)
```
