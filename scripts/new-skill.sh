#!/usr/bin/env bash
#
# Scaffold a new skill from templates/skill/ and wire it into the plugin.
#
# Usage:
#   ./scripts/new-skill.sh <skill-name> ["One-line description"]
#
# Example:
#   ./scripts/new-skill.sh somnio-skill-creator "Creates new Somnio Claude Code skills."
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$ROOT/templates/skill"
SKILLS_DIR="$ROOT/skills"
PLUGIN_SKILLS_DIR="$ROOT/plugins/somnio-ai-solutions/skills"

NAME="${1:-}"
DESCRIPTION="${2:-<One-line summary of what this skill produces and for whom.>}"

if [[ -z "$NAME" ]]; then
  echo "usage: $0 <skill-name> [\"One-line description\"]" >&2
  exit 2
fi

if ! printf '%s' "$NAME" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "error: '$NAME' must be kebab-case (lowercase letters, digits, single dashes)" >&2
  exit 1
fi

if [[ ${#NAME} -gt 64 ]]; then
  echo "error: skill name is ${#NAME} chars, max is 64" >&2
  exit 1
fi

SKILL_DIR="$SKILLS_DIR/$NAME"
if [[ -e "$SKILL_DIR" ]]; then
  echo "error: $SKILL_DIR already exists" >&2
  exit 1
fi

TITLE="$(printf '%s' "$NAME" | tr '-' ' ' \
  | awk '{for (i = 1; i <= NF; i++) $i = toupper(substr($i, 1, 1)) substr($i, 2)} 1')"

mkdir -p "$SKILLS_DIR"
cp -R "$TEMPLATE_DIR" "$SKILL_DIR"
find "$SKILL_DIR" -name '.gitkeep' -delete

SKILL_NAME="$NAME" SKILL_TITLE="$TITLE" SKILL_DESCRIPTION="$DESCRIPTION" \
  python3 - "$SKILL_DIR/SKILL.md" <<'PY'
import os
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as handle:
    text = handle.read()

for key in ("SKILL_NAME", "SKILL_TITLE", "SKILL_DESCRIPTION"):
    text = text.replace("{{%s}}" % key, os.environ[key])

with open(path, "w", encoding="utf-8") as handle:
    handle.write(text)
PY

mkdir -p "$PLUGIN_SKILLS_DIR"
ln -sfn "../../../skills/$NAME" "$PLUGIN_SKILLS_DIR/$NAME"

python3 "$ROOT/scripts/sync-readme.py" >/dev/null

cat <<EOF
Created skills/$NAME

  skills/$NAME/SKILL.md                              edit this first
  skills/$NAME/scripts/                              executable helpers (optional)
  skills/$NAME/references/                           long-form material (optional)
  plugins/somnio-ai-solutions/skills/$NAME           symlink -> skills/$NAME
  README.md                                          skills table regenerated

Next:
  1. Write the frontmatter description — it is what makes Claude load the skill.
  2. Fill in the workflow in skills/$NAME/SKILL.md and delete the authoring notes.
  3. Run 'make check' before opening the pull request.
EOF
