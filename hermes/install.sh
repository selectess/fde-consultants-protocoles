#!/usr/bin/env bash
# FDE Consultant Skill — Hermes installer
# This script installs the FDE Consultant Skill into the Hermes agent
# environment at ~/.hermes/skills/fde-consultant/
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_SOURCE="$REPO_DIR/skill"
SKILL_NAME="fde-consultant"
HERMES_SKILLS_DIR="${HERMES_HOME:-$HOME/.hermes}/skills"
TARGET="$HERMES_SKILLS_DIR/$SKILL_NAME"

echo "FDE Consultant - Hermes installer"
echo "  Source: $SKILL_SOURCE"
echo "  Target: $TARGET"

if [ ! -f "$SKILL_SOURCE/SKILL.md" ]; then
  echo "ERROR: $SKILL_SOURCE/SKILL.md not found. Run from the FDE Consultant repo root."
  exit 1
fi

mkdir -p "$HERMES_SKILLS_DIR"

# Symlink the entire skill/ tree so updates flow automatically
if [ -L "$TARGET" ]; then
  rm "$TARGET"
fi
if [ -d "$TARGET" ]; then
  echo "  Removing existing $TARGET..."
  rm -rf "$TARGET"
fi

ln -s "$SKILL_SOURCE" "$TARGET"
echo "  -> Symlinked $SKILL_SOURCE to $TARGET"

# Optional: install the Modex runtime (multi-agent)
MODEX_SOURCE="$REPO_DIR/modex"
if [ -d "$MODEX_SOURCE" ]; then
  MODEX_TARGET="$HERMES_SKILLS_DIR/fde-modex"
  if [ -L "$MODEX_TARGET" ]; then rm "$MODEX_TARGET"; fi
  ln -s "$MODEX_SOURCE" "$MODEX_TARGET"
  echo "  -> Symlinked Modex to $MODEX_TARGET"
fi

echo ""
echo "Installation complete."
echo ""
echo "Hermes will auto-discover the FDE Consultant Skill on next agent invocation."
echo "To force reload, restart the Hermes daemon."
