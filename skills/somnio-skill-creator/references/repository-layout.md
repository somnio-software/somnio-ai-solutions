# Somnio Skills Repository Layout

Every `somnio-*-ai` repository follows this shape, so a skill written in one is
installable from any other without rework.

## Contents

- Directory layout
- Why the plugin uses symlinks
- The marketplace manifest
- Packaging is CI's job
- Adding a skill to an area repository

---

## Directory layout

```
<repo>/
├── CLAUDE.md                             # Repo-wide rules for Claude Code
├── README.md                             # Index; skills table generated between markers
├── .claude-plugin/
│   └── marketplace.json                  # Makes the repo installable as a marketplace
├── skills/                               # Source of truth — one folder per skill
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/                      # Executed, never loaded into context
│       ├── references/                   # Read on demand, one level deep
│       └── assets/                       # Templates and static files
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json    # Plugin manifest
        └── skills/<skill-name>           # Symlink -> ../../../skills/<skill-name>
```

Repositories with several departments keep one plugin per department
(`plugins/engineering-management/`, `plugins/qa-management/`); a single-audience
repository keeps one plugin covering everything.

---

## Why the plugin uses symlinks

`skills/` is the only place a skill is edited. The plugin folder holds symlinks
pointing back at it, so:

- there is never a stale second copy to keep in sync;
- a skill can belong to more than one plugin at once;
- `zip` dereferences symlinks when packaging, so the archive is self-contained.

Create them from the repository root:

```bash
ln -s ../../../skills/<skill-name> plugins/<plugin-name>/skills/<skill-name>
```

A copy instead of a symlink is a validation error, not a style preference.

---

## The marketplace manifest

`.claude-plugin/marketplace.json` at the repository root turns the repo into a
Claude Code marketplace, so a teammate installs it without cloning:

```bash
/plugin marketplace add somnio-software/<repo-name>
/plugin install <plugin-name>@<marketplace-name>
```

Add every plugin of the repository to its `plugins` array.

---

## Packaging is CI's job

Claude Desktop (Cowork) needs a `.zip`, and that archive is built and committed
by GitHub Actions whenever anything under `skills/` or `plugins/` changes on
`main`. Do not build it by hand as part of normal work.

The exact command CI runs, for reference and for local debugging:

```bash
cd plugins
zip -r <plugin-name>.zip <plugin-name>/ \
  --exclude "*.DS_Store" \
  --exclude "*/.venv/*" \
  --exclude "*/.ruff_cache/*" \
  --exclude "*/__pycache__/*" \
  --exclude "*/.git/*"
```

The archive lands next to the plugin directory as `plugins/<plugin-name>.zip`.

---

## Adding a skill to an area repository

The creator script works against any repository root, so a skill can be created
in an area repo from this one:

```bash
python3 skills/somnio-skill-creator/scripts/scaffold_skill.py <skill-name> \
  --repo-root ../somnio-finance-ai \
  --description "..."
```

It detects the plugins of that repository, creates the symlinks with the right
depth, and syncs that repository's README table if it carries the markers.
