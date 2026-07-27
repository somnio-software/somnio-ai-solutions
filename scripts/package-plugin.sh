#!/usr/bin/env bash
#
# Build plugins/somnio-ai-solutions.zip for upload to Claude Desktop (Cowork).
# Symlinked skills are dereferenced, so the archive is self-contained.
#
# Usage:
#   ./scripts/package-plugin.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_NAME="somnio-ai-solutions"

command -v zip >/dev/null 2>&1 || { echo "error: 'zip' is not installed" >&2; exit 1; }

cd "$ROOT/plugins"
rm -f "$PLUGIN_NAME.zip"

zip -r "$PLUGIN_NAME.zip" "$PLUGIN_NAME/" \
  --exclude "*.DS_Store" \
  --exclude "*/.venv/*" \
  --exclude "*/.ruff_cache/*" \
  --exclude "*/__pycache__/*" \
  --exclude "*/.git/*" \
  --exclude "*/.gitkeep"

echo
echo "Built plugins/$PLUGIN_NAME.zip"
echo "Upload it in Claude Desktop → Cowork → Customize → Browse plugins → Upload a custom plugin file."
