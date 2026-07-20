#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADAPTER="${ROOT}/scripts/termux-adapter.py"

usage() {
  cat <<'USAGE'
usage: pleiades-factory-tools <validate|plan|pin|lock|sync|status> [args]

`pin` records the exact clean canonical factory-stack commit and catalog/toolchain
hashes. `lock` and `sync` require that source pin to match. This adapter never
exposes hardcoded execution commands for cloned third-party projects.
USAGE
}

case "${1:-}" in
  validate|plan|pin|lock|sync|status)
    command="$1"
    shift
    exec python3 "$ADAPTER" "$command" "$@"
    ;;
  --help|-h|"") usage ;;
  *) usage >&2; exit 2 ;;
esac
