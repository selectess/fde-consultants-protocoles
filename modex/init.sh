#!/usr/bin/env bash
# ==============================================================================
# FDE Modex -- Memory Bootstrap (Industrial-grade)
# ==============================================================================
# Usage:
#   bash modex/init.sh                  # bootstraps ./fde-memory/
#   bash modex/init.sh /path/to/project # bootstraps another project
#
# Creates:
#   fde-memory/
#     ├── context.json         # mutable current state (6-Q, claim, stage)
#     ├── trust-score.json     # append-only certification log
#     ├── lessons.json         # mutable lessons learned
#     └── episodes/            # private dir, NOT tracked by git
# ==============================================================================
set -euo pipefail

PROJECT_ROOT="${1:-.}"
MEM_DIR="$PROJECT_ROOT/fde-memory"
EPISODES_DIR="$MEM_DIR/episodes"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -d "$MEM_DIR" ]; then
  echo -e "${YELLOW}⚠ fde-memory/ already exists at $MEM_DIR${NC}"
  echo "   This script will NOT overwrite existing files."
  echo "   Delete the directory manually if you want a fresh start."
  exit 0
fi

mkdir -p "$EPISODES_DIR"

# Genesis timestamp (ISO 8601 UTC)
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# context.json — mutable current state
cat > "$MEM_DIR/context.json" <<EOF
{
  "schema": "fde-context-v1",
  "created_at": "$NOW",
  "updated_at": "$NOW",
  "current_stage": "scoping",
  "stakeholders": [],
  "last_claim": null,
  "open_questions": []
}
EOF

# trust-score.json — append-only certification log
cat > "$MEM_DIR/trust-score.json" <<EOF
{
  "schema": "fde-trust-score-v1",
  "created_at": "$NOW",
  "last_verdict": null,
  "history": []
}
EOF

# lessons.json — mutable lessons learned
cat > "$MEM_DIR/lessons.json" <<EOF
{
  "schema": "fde-scientific-search-lessons-v1",
  "created_at": "$NOW",
  "lessons": []
}
EOF

# Episodes dir is intentionally empty (private)
cat > "$EPISODES_DIR/.gitkeep" <<EOF
# Keep this dir under git. .gitkeep is the convention.
# Real episode files (one per stage or per engagement) are gitignored.
EOF

echo -e "${GREEN}✓ fde-memory/ bootstrapped at $MEM_DIR${NC}"
echo "  - context.json       (mutable)"
echo "  - trust-score.json   (append-only certifications)"
echo "  - lessons.json       (rejected hypotheses)"
echo "  - episodes/          (private — gitignored)"
echo ""
echo "Next step: produce a deliverable, then run:"
echo "  bash modex/verify.sh  $PROJECT_ROOT"
