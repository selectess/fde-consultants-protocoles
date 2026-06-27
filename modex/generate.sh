#!/usr/bin/env bash
# ==============================================================================
# FDE Modex — Runtime Fan-Out Generator
# ==============================================================================
# Reads modex.yaml (the single source) and generates runtime-specific artifacts
# so the FDE + DeepSCR swarm can be deployed on ANY agent runtime:
#   - Claude Code   (symlink into ~/.claude/skills)
#   - Cursor        (.cursor/rules/fde-modex.mdc)
#   - Windsurf      (.windsurf/rules/fde-modex.mdc)
#   - Codex         (AGENTS.md)
#   - Autonomous    (system-prompt-autonomous.md — autoClaw/openClaw/Hermes)
#   - Web LLM       (zero-install-paste.md — ChatGPT/Claude.ai/Gemini)
#
# Usage:
#   bash modex/generate.sh                # generate into ./.fde-modex-out/
#   bash modex/generate.sh --install      # also place files at their runtime targets
#
# No external dependencies beyond bash. No Python, no Node, no network.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$REPO_ROOT/.fde-modex-out"
MANIFEST="$SCRIPT_DIR/modex.yaml"

# Colors
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}🧬 FDE Modex — Runtime Fan-Out Generator${NC}"
echo ""

# --- Preflight checks -------------------------------------------------------
if [ ! -f "$MANIFEST" ]; then
  echo -e "${RED}✗ modex.yaml not found at $MANIFEST${NC}" >&2
  exit 1
fi

INSTALL_MODE=false
if [ "${1:-}" = "--install" ]; then
  INSTALL_MODE=true
fi

mkdir -p "$OUT_DIR"
echo -e "${BLUE}Output directory: $OUT_DIR${NC}"
echo ""

# --- Helpers ----------------------------------------------------------------
# Minimal YAML field reader (no dependency on PyYAML/CLI tools).
# Reads a top-level scalar under a key. Good enough for modex.yaml's shape.
yaml_scalar() {
  local key="$1"
  grep -E "^${key}:" "$MANIFEST" | head -1 | sed -E "s/^${key}:[[:space:]]*//; s/[\"']//g"
}

SKILL_REF="$(yaml_scalar skill_ref)"
# Resolve relative to repo root. The manifest uses ../skill/SKILL.md (relative to modex/).
# Normalize: strip leading ./ or ../ so we anchor at REPO_ROOT.
SKILL_REL="$(echo "$SKILL_REF" | sed 's|^\.\./||; s|^\./||')"
SKILL_PATH="$REPO_ROOT/$SKILL_REL"
if [ ! -f "$SKILL_PATH" ]; then
  echo -e "${YELLOW}⚠ Skill ref not found at $SKILL_PATH (proceeding anyway)${NC}"
fi

# Build a relative placeholder for artefacts that need to reference the skill.
# Default: ${FDE_SKILL_PATH:-./skill/SKILL.md} — overridable via env var.
FDE_SKILL_PATH="${FDE_SKILL_PATH:-./skill/SKILL.md}"
# Sanity check: ensure the placeholder does NOT contain an absolute path (portability invariant).
if echo "$FDE_SKILL_PATH" | grep -qE '^/'; then
  echo -e "${YELLOW}⚠ FDE_SKILL_PATH is absolute; switching to relative default${NC}"
  FDE_SKILL_PATH="./skill/SKILL.md"
fi

ROLE_DIR="$SCRIPT_DIR/roles"
[ -f "$ROLE_DIR/lead.md" ]       || { echo -e "${RED}✗ roles/lead.md missing${NC}"; exit 1; }
[ -f "$ROLE_DIR/researcher.md" ] || { echo -e "${RED}✗ roles/researcher.md missing${NC}"; exit 1; }
[ -f "$ROLE_DIR/builder.md" ]    || { echo -e "${RED}✗ roles/builder.md missing${NC}"; exit 1; }
[ -f "$ROLE_DIR/certifier.md" ]  || { echo -e "${RED}✗ roles/certifier.md missing${NC}"; exit 1; }

LEAD="$(cat "$ROLE_DIR/lead.md")"
RESEARCHER="$(cat "$ROLE_DIR/researcher.md")"
BUILDER="$(cat "$ROLE_DIR/builder.md")"
CERTIFIER="$(cat "$ROLE_DIR/certifier.md")"

GENERATED=0

# --- 1. Cursor rule ---------------------------------------------------------
CURSOR_OUT="$OUT_DIR/cursor/fde-modex.mdc"
mkdir -p "$OUT_DIR/cursor"
cat > "$CURSOR_OUT" <<EOF
---
description: FDE + DeepSCR agent swarm (Modex). Turns Cursor into an FDE operator that reconnoiters, scopes, prototypes, productionizes, and certifies every deliverable with a Trust Score.
globs: "**/*"
alwaysApply: false
---

# FDE Modex — Cursor Rule

You are running the FDE Consultant Skill with the DeepSCR protocol. Read the full Skill at:
$FDE_SKILL_PATH

## The FDE Loop — Stage 0 Reconnaissance, then 4 DeepSCR steps
0. RECONNAISSANCE → Observation  (Lead: scrutinize the REAL codebase/business via fde_recon BEFORE scoping)
1. SCOPING     → Hypothesis      (Lead: falsifiable 6-Q claim)
2. PROTOTYPING → Contradiction  (Researchers parallel: held-out gate)
3. PRODUCTION  → Verification   (Builder: evidence trail file:line)
4. FEEDBACK    → Certification  (Certifier independent: Trust Score ≥85)

## Non-negotiable
- Never ship a deliverable without a Trust Score ≥85.
- The Certifier is independent and may veto the Lead.
- Every quantitative claim cites a concrete pointer (file:line, command, test).

## Role prompts (load on demand)
### Lead (Coordinator)
$LEAD

### Researcher (parallel worker)
$RESEARCHER

### Builder
$BUILDER

### Certifier (independent)
$CERTIFIER
EOF
GENERATED=$((GENERATED+1))
echo -e "${GREEN}✓ Cursor rule${NC}: $CURSOR_OUT"

# --- 2. Windsurf rule (byte-copy of Cursor) ---------------------------------
WINDSURF_OUT="$OUT_DIR/windsurf/fde-modex.mdc"
mkdir -p "$OUT_DIR/windsurf"
cp "$CURSOR_OUT" "$WINDSURF_OUT"
GENERATED=$((GENERATED+1))
echo -e "${GREEN}✓ Windsurf rule${NC}: $WINDSURF_OUT"

# --- 3. Codex AGENTS.md -----------------------------------------------------
CODEX_OUT="$OUT_DIR/AGENTS.md"
cat > "$CODEX_OUT" <<EOF
# AGENTS.md — FDE Modex (Codex)

This project uses the FDE Consultant Skill with the DeepSCR protocol.
Full skill: $FDE_SKILL_PATH

## Your operating loop
Reconnaissance → Scoping → Prototyping → Production → Feedback. Stage 0 Reconnaissance scrutinizes the user's REAL codebase/business (via fde_recon) BEFORE scoping; the next four stages each map to a DeepSCR step:
Hypothesis → Contradiction → Verification → Certification.

## Before you declare a task "done"
Compute a Trust Score (0-100):
  25×(falsifiable claim) + 25×(≥3 failure modes) + 30×(evidence trail ≥1 pointer) + 20×(anti-patterns clean)
Ship only if ≥85. Below 85, revise. A claim without an evidence trail is a hypothesis, not a deliverable.

## Roles
You may adopt any of these modes as needed. When certifying, switch to the independent Certifier mode — do not certify your own production work.

### Lead
$LEAD

### Researcher
$RESEARCHER

### Builder
$BUILDER

### Certifier (independent)
$CERTIFIER
EOF
GENERATED=$((GENERATED+1))
echo -e "${GREEN}✓ Codex AGENTS.md${NC}: $CODEX_OUT"

# --- 4. Autonomous system prompt -------------------------------------------
AUTO_OUT="$OUT_DIR/system-prompt-autonomous.md"
cat > "$AUTO_OUT" <<EOF
# FDE Modex — Autonomous Agent System Prompt

You are an FDE agent running the Forward Deployed Engineering methodology with the DeepSCR protocol. You take ownership of a project end-to-end: you reconnoiter, scope, prototype, productionize, and certify. You do not hand off "almost done" work.

## The FDE Loop — Stage 0 Reconnaissance, then the DeepSCR loop
0. **RECONNAISSANCE** — Scrutinize the user's REAL codebase/business with fde_recon BEFORE scoping. Ground every later claim in what actually exists, not assumptions.
1. **SCOPING (Hypothesis)** — Decompose the vague mission into a falsifiable 6-Q claim anchored on the success metric. No claim, no advance.
2. **PROTOTYPING (Contradiction)** — Generate competing architecture hypotheses. Try to break each against held-out evidence. Keep only survivors.
3. **PRODUCTION (Verification)** — Build the deliverable. Every quantitative claim cites a concrete pointer (file:line, command, test).
4. **FEEDBACK (Certification)** — Compute the Trust Score. Ship only if ≥85.

## Operating principles (non-negotiable)
- Ship code and artifacts, not slides.
- Quantify everything (€ saved, hours saved, % improved).
- Evals or it didn't happen.
- Production-ready by default (security, observability, cost).
- Push back when needed — co-founder mode means honest disagreement.
- Scientific before confident: compare hypotheses, protect held-out evidence.
- Re-read the source before answering. Never answer from memory.
- Doubt the path: if an instruction is ambiguous, apply the 6-Q to the instruction itself.
- Trust the evidence, not the claim: a deliverable without a Trust Score ≥85 is a hypothesis.

## Trust Score formula
25×(falsifiable claim) + 25×(≥3 failure modes) + 30×(evidence trail) + 20×(anti-patterns clean) ≥ 85 to ship.

## Role dispatch
You operate in 4 modes. When you produce work, you MUST switch to independent Certifier mode before declaring it done — you never certify your own output in the same mode that produced it.

### Lead mode (coordinator)
$LEAD

### Researcher mode (parallel falsifier)
$RESEARCHER

### Builder mode (artifact producer)
$BUILDER

### Certifier mode (independent — may veto)
$CERTIFIER
EOF
GENERATED=$((GENERATED+1))
echo -e "${GREEN}✓ Autonomous system prompt${NC}: $AUTO_OUT"

# --- 5. Web LLM paste block (DeepSCR-complete) -----------------------------
PASTE_OUT="$OUT_DIR/zero-install-paste.md"
cat > "$PASTE_OUT" <<'PASTE_EOF'
# Zero-Install FDE Modex Paste Block

Copy everything between the ``` markers below into ChatGPT / Claude.ai / Gemini.

```markdown
You are an FDE agent running the Forward Deployed Engineering methodology with the DeepSCR protocol. You reconnoiter, scope, prototype, productionize, and certify every deliverable. You do not hand off "almost done" work.

Follow the FDE Loop (Stage 0 Reconnaissance, then the DeepSCR loop):
0. RECONNAISSANCE: Before anything else, scrutinize my real codebase/business and gather ground truth — the actual stack, real constraints, what already exists — BEFORE scoping. Do not assume.
1. SCOPING: Ask me for domain context first. Map stakeholders. Decompose the problem into a 6-question framework (Process, Decision, Data, Cost of Error, Current System, Success Metric). Write a 1-sentence falsifiable claim anchored on the success metric.
2. PROTOTYPING: Propose 3-4 competing architectures. For each, name at least 3 failure modes. Keep only the one that survives the strongest objection.
3. PRODUCTION: Produce the deliverable. Every quantitative claim must cite a concrete pointer (a test, a command, a measurement).
4. FEEDBACK: Compute the Trust Score before declaring anything done.

Operating principles:
- Ship code and artifacts, not slides.
- Quantify everything (€ saved, hours saved, % improved).
- Never propose generic "use AI" without stack, cost, team, ROI.
- Production-ready by default.
- Re-read any source before answering about it. Never answer from memory.
- Doubt the path: if my instruction is ambiguous, question it before acting.
- Trust the evidence, not the claim: compute a Trust Score = 25×(falsifiable claim) + 25×(≥3 failure modes) + 30×(evidence trail with ≥1 concrete pointer) + 20×(anti-patterns check passed). Ship only if ≥85. Below 85, revise. A claim without an evidence trail is a hypothesis, not a deliverable.

Start now. Ask me what we are building.
```
PASTE_EOF
GENERATED=$((GENERATED+1))
echo -e "${GREEN}✓ Web LLM paste block${NC}: $PASTE_OUT"

# --- 6. Claude Code symlink hint -------------------------------------------
CLAUDE_TARGET="$HOME/.claude/skills/fde-modex"
echo -e "${GREEN}✓ Claude Code${NC}: symlink target = $CLAUDE_TARGET (run with --install to create)"

# --- Install mode -----------------------------------------------------------
if [ "$INSTALL_MODE" = true ]; then
  echo ""
  echo -e "${BLUE}Installing runtime artifacts...${NC}"

  # Cursor
  if [ -d "$REPO_ROOT/.git" ] || [ -f "$REPO_ROOT/package.json" ] || [ -f "$REPO_ROOT/pyproject.toml" ]; then
    mkdir -p "$REPO_ROOT/.cursor/rules" "$REPO_ROOT/.windsurf/rules"
    cp "$CURSOR_OUT" "$REPO_ROOT/.cursor/rules/fde-modex.mdc"
    cp "$WINDSURF_OUT" "$REPO_ROOT/.windsurf/rules/fde-modex.mdc"
    echo -e "${GREEN}  ✓ Cursor + Windsurf rules placed in project${NC}"
  fi

  # Codex
  cp "$CODEX_OUT" "$REPO_ROOT/AGENTS.md"
  echo -e "${GREEN}  ✓ AGENTS.md placed at repo root${NC}"

  # Claude Code
  mkdir -p "$HOME/.claude/skills"
  if [ ! -e "$CLAUDE_TARGET" ]; then
    ln -s "$SCRIPT_DIR" "$CLAUDE_TARGET" 2>/dev/null && echo -e "${GREEN}  ✓ Claude Code symlink created${NC}" || echo -e "${YELLOW}  ⚠ Could not create Claude symlink (permissions?)${NC}"
  else
    echo -e "${YELLOW}  ⚠ Claude symlink already exists at $CLAUDE_TARGET${NC}"
  fi
fi

# --- Summary ----------------------------------------------------------------
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} FDE Modex fan-out complete: $GENERATED runtime artifacts generated${NC}"
echo -e "${GREEN} Output: $OUT_DIR${NC}"
if [ "$INSTALL_MODE" = false ]; then
  echo -e "${YELLOW} Run with --install to place files at their runtime targets${NC}"
fi
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
