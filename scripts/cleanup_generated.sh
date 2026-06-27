#!/usr/bin/env bash
# Dry-run by default cleanup for generated local artifacts.
# Use --apply to delete cache/noise files. Use --include-db with --apply to also
# remove local SQLite/auth DB files.

set -euo pipefail

APPLY=false
INCLUDE_DB=false

usage() {
  cat <<'USAGE'
Usage: scripts/cleanup_generated.sh [--apply] [--include-db]

Default mode is dry-run. It prints what would be removed.

Options:
  --apply       Actually remove generated cache/noise artifacts.
  --include-db  Include local *.db/*.sqlite files. Requires --apply to delete.
  -h, --help    Show this help.

Examples:
  scripts/cleanup_generated.sh
  scripts/cleanup_generated.sh --apply
  scripts/cleanup_generated.sh --apply --include-db
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      APPLY=true
      shift
      ;;
    --include-db)
      INCLUDE_DB=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CACHE_TARGETS=()
while IFS= read -r target; do
  CACHE_TARGETS+=("$target")
done < <(
  find . \
    \( -name '.pytest_cache' -o -name '__pycache__' -o -name '.DS_Store' -o -name '.coverage' -o -name 'htmlcov' \) \
    -print | sort
)

DB_TARGETS=()
while IFS= read -r target; do
  DB_TARGETS+=("$target")
done < <(
  find . \
    \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) \
    -print | sort
)

print_targets() {
  local label="$1"
  shift
  local targets=("$@")
  echo "$label"
  if [[ ${#targets[@]} -eq 0 ]]; then
    echo "  none"
    return
  fi
  printf '  %s\n' "${targets[@]}"
}

echo "FDE Consultant generated-artifact cleanup"
echo "Root: $ROOT"
echo "Mode: $([[ "$APPLY" == true ]] && echo apply || echo dry-run)"
echo

print_targets "Cache/noise targets:" "${CACHE_TARGETS[@]}"
echo
if [[ "$INCLUDE_DB" == true ]]; then
  print_targets "Local DB targets:" "${DB_TARGETS[@]}"
else
  echo "Local DB targets: skipped (pass --include-db to include)"
  if [[ ${#DB_TARGETS[@]} -gt 0 ]]; then
    printf '  %s\n' "${DB_TARGETS[@]}"
  fi
fi

if [[ "$APPLY" != true ]]; then
  echo
  echo "Dry-run only. Re-run with --apply to remove cache/noise targets."
  echo "Add --include-db only if you intentionally want to remove local DB state."
  exit 0
fi

remove_targets=("${CACHE_TARGETS[@]}")
if [[ "$INCLUDE_DB" == true ]]; then
  remove_targets+=("${DB_TARGETS[@]}")
fi

if [[ ${#remove_targets[@]} -eq 0 ]]; then
  echo
  echo "Nothing to remove."
  exit 0
fi

echo
echo "Removing ${#remove_targets[@]} target(s)..."
rm -rf -- "${remove_targets[@]}"
echo "Cleanup complete."
