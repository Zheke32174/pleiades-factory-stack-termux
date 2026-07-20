#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADAPTER="${ROOT}/scripts/termux-adapter.py"

usage() {
  cat <<'USAGE'
usage: bootstrap-tools.sh <validate|plan|pin|lock|sync|status> [canonical toolchain args]

Examples:
  bootstrap-tools.sh plan
  bootstrap-tools.sh pin       # review and pin exact canonical factory source
  bootstrap-tools.sh lock      # requires a matching canonical-source pin
  bootstrap-tools.sh sync      # requires source pin and exact upstream locks
  bootstrap-tools.sh sync --floating   # source pin still required

The default no-argument action is `plan`; source is never cloned implicitly.
A `--floating` upstream sync does not bypass canonical factory-source identity.
USAGE
}

case "${1:-plan}" in
  validate|plan|pin|lock|sync|status)
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
