#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="${ROOT}/scripts/termux-adapter.py"

usage() {
  cat <<'USAGE'
usage: bootstrap-tools.sh <plan|lock|sync|status> [canonical toolchain args]

Examples:
  bootstrap-tools.sh plan
  bootstrap-tools.sh lock
  bootstrap-tools.sh sync
  bootstrap-tools.sh sync --floating   # explicit unpinned escape hatch

The default no-argument action is `plan`; source is never cloned implicitly.
USAGE
}

case "${1:-plan}" in
  plan|lock|sync|status|validate)
    command="${1:-plan}"
    [[ $# -gt 0 ]] && shift
    exec python3 "$ADAPTER" "$command" "$@"
    ;;
  --help|-h)
    usage
    ;;
  *)
    echo "bootstrap-tools: unknown action: $1" >&2
    usage >&2
    exit 2
    ;;
esac
