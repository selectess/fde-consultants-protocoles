#!/usr/bin/env bash
# ==============================================================================
# FDE Modex — Trust Score Gate (industrial-grade)
# ==============================================================================
# Usage:
#   bash modex/verify.sh                          # checks ./fde-memory/trust-score.json
#   bash modex/verify.sh /path/to/project         # checks another project
#   bash modex/verify.sh --score=92 --sha=<hash>  # inline check (no file)
#
# Exits:
#   0 = PASS (Trust Score ≥85 + SHA-256 valid)
#   1 = FAIL (any reason)
#   2 = NO_CERTIFICATION (no trust-score.json or no last_verdict)
# ==============================================================================
set -euo pipefail

PROJECT_ROOT="."
INLINE_SCORE=""
INLINE_SHA=""
MODE_REGISTRY=""

# Parse args
for arg in "$@"; do
  case "$arg" in
    --score=*) INLINE_SCORE="${arg#--score=}" ;;
    --sha=*)   INLINE_SHA="${arg#--sha=}" ;;
    --registry) MODE_REGISTRY=1 ;;
    --help|-h)
      grep "^# " "$0" | sed 's/^# //'
      exit 0
      ;;
    /*) PROJECT_ROOT="$arg" ;;
  esac
done

# --- Registry chain verification (public proof) ------------------------------
if [ -n "$MODE_REGISTRY" ]; then
  if python3 - <<'PYEOF'
import json, hashlib, sys, pathlib
root = pathlib.Path('.')
try:
    idx = json.loads((root / 'registry' / 'index.json').read_text())
except Exception as e:
    print(f"\033[0;31m✗ FAIL\033[0m: cannot read registry/index.json: {e}"); sys.exit(1)
prev, ok, n = None, True, 0
for e in idx.get('entries', []):
    raw = (root / e['path']).read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if h != e.get('sha256'):
        print(f"\033[0;31m✗ FAIL\033[0m: {e['cert_id']}: content hash != index sha256"); ok = False; continue
    ph = json.loads(raw).get('prev_hash')
    if prev is not None and ph != prev:
        print(f"\033[0;31m✗ FAIL\033[0m: {e['cert_id']}: prev_hash breaks the chain"); ok = False
    prev, n = h, n + 1
if ok:
    print(f"\033[0;32m✓ OK\033[0m: registry chain valid — {n} entries, content-hashed and prev-hash-linked")
sys.exit(0 if ok else 1)
PYEOF
  then exit 0; else exit 1; fi
fi

MEM_DIR="$PROJECT_ROOT/fde-memory"
TS_FILE="$MEM_DIR/trust-score.json"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Inline check path -------------------------------------------------------
if [ -n "$INLINE_SCORE" ]; then
  if [ "$INLINE_SCORE" -lt 85 ]; then
    echo -e "${RED}✗ FAIL${NC}: Trust Score $INLINE_SCORE < 85"
    exit 1
  fi
  if [ -z "$INLINE_SHA" ] || [ "${#INLINE_SHA}" -ne 64 ]; then
    echo -e "${RED}✗ FAIL${NC}: SHA-256 missing or malformed: '$INLINE_SHA'"
    exit 1
  fi
  echo -e "${GREEN}✓ OK${NC}: Trust Score $INLINE_SCORE/100, SHA-256 ${INLINE_SHA:0:12}..."
  exit 0
fi

# --- File-based check --------------------------------------------------------
if [ ! -d "$MEM_DIR" ]; then
  echo -e "${RED}✗ FAIL${NC}: fde-memory/ does not exist. Run 'bash modex/init.sh' first."
  exit 1
fi

if [ ! -f "$TS_FILE" ]; then
  echo -e "${RED}✗ FAIL${NC}: $TS_FILE missing. Run 'bash modex/init.sh' or write a Trust Score manually."
  exit 1
fi

# Parse JSON without dependency on jq (use python3 or node — both usually present).
LAST_VERDICT=$(python3 -c "
import json, sys
try:
    with open('$TS_FILE') as f:
        data = json.load(f)
    v = data.get('last_verdict')
    if v is None:
        sys.exit(11)  # no certification yet
    print(v.get('score', ''))
    print(v.get('sha256', ''))
except Exception as e:
    sys.stderr.write(str(e))
    sys.exit(1)
") || {
  EXIT_CODE=$?
  if [ "$EXIT_CODE" -eq 11 ]; then
    echo -e "${YELLOW}⚠ NO_CERTIFICATION${NC}: trust-score.json has no last_verdict yet."
    exit 2
  fi
  echo -e "${RED}✗ FAIL${NC}: could not parse trust-score.json (exit $EXIT_CODE)"
  exit 1
}

SCORE=$(echo "$LAST_VERDICT" | sed -n '1p')
SHA=$(echo "$LAST_VERDICT" | sed -n '2p')

if [ -z "$SCORE" ] || [ "$SCORE" -lt 85 ]; then
  echo -e "${RED}✗ FAIL${NC}: Trust Score ${SCORE:-<empty>} < 85"
  exit 1
fi

if [ -z "$SHA" ] || [ "${#SHA}" -ne 64 ]; then
  echo -e "${RED}✗ FAIL${NC}: SHA-256 missing or malformed: '$SHA'"
  exit 1
fi

echo -e "${GREEN}✓ OK${NC}: Trust Score $SCORE/100, SHA-256 ${SHA:0:12}..."
exit 0
