#!/usr/bin/env bash
# ==============================================================================
# FDE Consultant — one-command, multi-runtime Skill installer
# ==============================================================================
# Installs the FDE+DeepSCR Skill into every AI agent runtime detected on this
# machine. `SKILL.md` is a cross-runtime standard (agentskills.io), so the same
# skill folder works everywhere — only the destination + activation differ.
#
#   Install   :  bash install.sh            (all detected runtimes)
#   Uninstall :  bash install.sh --uninstall
#   One target:  bash install.sh claude-code | codex | hermes | openclaw | claude-app
#
# Native filesystem install (auto): Claude Code, Codex, Hermes, openclaw.
# Manual (upload-only): Claude desktop/claude.ai app  -> we build a .zip for you.
# ==============================================================================
set -uo pipefail

G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; R='\033[0;31m'; D='\033[2m'; X='\033[0m'
SKILL_NAME="fde-consultant"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/skill"

MODE="install"; ONLY=""
for a in "$@"; do
  case "$a" in
    --uninstall) MODE="uninstall" ;;
    claude-code|codex|hermes|openclaw|claude-app) ONLY="$a" ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  esac
done

if [ ! -f "$SKILL_SRC/SKILL.md" ]; then
  echo -e "${R}✗ $SKILL_SRC/SKILL.md not found — run this from the FDE Consultant repo.${X}"; exit 1
fi

echo -e "${B}FDE Consultant — Skill ${MODE}${X}  ${D}(source: $SKILL_SRC)${X}\n"
DONE=()

want() { [ -z "$ONLY" ] || [ "$ONLY" = "$1" ]; }

# Symlink the skill folder into <dir>/<name> (single editable source; updates propagate)
link_into() {
  local label="$1" dir="$2" activate="${3:-}"
  if [ "$MODE" = "uninstall" ]; then
    if [ -e "$dir/$SKILL_NAME" ] || [ -L "$dir/$SKILL_NAME" ]; then
      rm -rf "$dir/$SKILL_NAME"; echo -e "  ${Y}↩ removed${X}  $label  ${D}($dir/$SKILL_NAME)${X}"; DONE+=("$label")
    fi
    return
  fi
  mkdir -p "$dir" 2>/dev/null || { echo -e "  ${D}· skipped $label (cannot write $dir)${X}"; return; }
  ln -sfn "$SKILL_SRC" "$dir/$SKILL_NAME"
  echo -e "  ${G}✅ $label${X}  ${D}→ $dir/$SKILL_NAME${X}"
  DONE+=("$label")
  [ -n "$activate" ] && eval "$activate" >/dev/null 2>&1 || true
}

# 1. Claude Code CLI  — ~/.claude/skills/  (native, hot-reload)
if want claude-code && { [ -d "$HOME/.claude" ] || command -v claude >/dev/null 2>&1; }; then
  link_into "Claude Code (CLI)" "$HOME/.claude/skills"
fi

# 2. Codex CLI + app — ~/.agents/skills/  (native, auto-scanned)
if want codex && { command -v codex >/dev/null 2>&1 || [ -d "$HOME/.codex" ] || [ -d "$HOME/.agents" ]; }; then
  link_into "Codex (CLI + app)" "$HOME/.agents/skills"
fi

# 3. Hermes CLI — ~/.hermes/skills/  (native, auto-live)
if want hermes && { command -v hermes >/dev/null 2>&1 || [ -d "$HOME/.hermes" ]; }; then
  link_into "Hermes CLI" "$HOME/.hermes/skills"
fi

# 4. openclaw — ~/.openclaw/workspace/skills/  (native) + refresh
if want openclaw && { command -v openclaw >/dev/null 2>&1 || [ -d "$HOME/.openclaw" ]; }; then
  link_into "openclaw" "$HOME/.openclaw/workspace/skills" \
    "command -v openclaw >/dev/null 2>&1 && openclaw agent --message 'refresh skills' --thinking low"
fi

# 5. Claude desktop / claude.ai app — UI upload only -> build a .zip
if want claude-app && [ "$MODE" = "install" ]; then
  if command -v zip >/dev/null 2>&1; then
    mkdir -p "$SCRIPT_DIR/dist"
    ( cd "$SCRIPT_DIR" && rm -f "dist/$SKILL_NAME-skill.zip" && zip -qr "dist/$SKILL_NAME-skill.zip" skill -x '*/__pycache__/*' '*/.DS_Store' )
    echo -e "  ${Y}📦 Claude desktop/app (manual)${X}  ${D}→ dist/$SKILL_NAME-skill.zip${X}"
    echo -e "     ${D}Upload it: Claude → Customize → Skills → Upload a skill (needs Code execution ON).${X}"
    DONE+=("Claude app (zip ready)")
  fi
fi

echo ""
if [ ${#DONE[@]} -eq 0 ]; then
  echo -e "${Y}No runtime detected/changed.${X} Install a target explicitly, e.g. ${D}bash install.sh codex${X}"
else
  echo -e "${G}Done (${MODE})${X} — ${DONE[*]}"
fi
cat <<EOF

Try it:   /fde-consultant scope this project
Web LLMs: paste skill/ZERO-INSTALL.md into ChatGPT / Claude.ai / Gemini
Plugin:   /plugin marketplace add selectess/fde-consultants-protocoles  &&  /plugin install fde-consultant@fde-consultant
EOF
