#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADAPTER="${ROOT}/scripts/termux-adapter.py"

usage() {
  cat <<'USAGE'
usage: pleiades-factory-tools <validate|plan|lock|sync|status> [args]

This adapter manages the canonical Termux source profile. It does not expose
hardcoded direct execution commands for cloned third-party projects.
USAGE
}

case "${1:-}" in
  validate|plan|lock|sync|status)
    command="$1"
    shift
    exec python3 "$ADAPTER" "$command" "$@"
    ;;
  --help|-h|"") usage ;;
  *) usage >&2; exit 2 ;;
esac
