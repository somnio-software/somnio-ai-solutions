# Installation

All skills in this repository ship as a single plugin,
[`plugins/somnio-ai-solutions/`](../plugins/somnio-ai-solutions).

## Claude Code (recommended)

The repository root is a Claude Code marketplace
([`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)), so a
teammate installs it without cloning:

```bash
/plugin marketplace add somnio-software/somnio-ai-solutions
/plugin install somnio-ai-solutions@somnio-ai
```

Working on the repository locally? Point the marketplace at your clone instead:

```bash
/plugin marketplace add ./
/plugin install somnio-ai-solutions@somnio-ai
/reload-plugins
```

## Claude Desktop (Cowork)

Claude Desktop requires a `.zip`, and **CI builds it for you** — download the
committed `plugins/somnio-ai-solutions.zip` from `main`, then:

1. Open **Claude Desktop** → **Cowork** tab
2. Click **Customize** in the left sidebar
3. Click **Browse plugins**
4. Select **Upload a custom plugin file** and choose the `.zip`

The plugin is saved locally to your machine. Repeat whenever the archive is
updated on `main`.

### Building the archive locally

Only for debugging an upload — never commit the result, since
[the pipeline](pipeline.md) rebuilds and commits it on merge:

```bash
make zip
```

That validates first, then runs the `zip` command documented in
[`CLAUDE.md`](../CLAUDE.md) from the `plugins/` directory so the archive contains
the plugin folder at its root. `zip` dereferences the skill symlinks, so the
archive is self-contained; confirm with `unzip -l` that every skill's `SKILL.md`
is inside.

## Verifying the install

Ask Claude Code for one of the skills by name — `somnio-skill-creator` or
`somnio-skill-verifier`. If nothing triggers, the plugin is not installed in that
session; `/reload-plugins` after a local marketplace change.
