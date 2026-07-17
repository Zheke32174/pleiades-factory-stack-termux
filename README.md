# Pleiades Factory Stack — Termux Adapter

This repository is the Android/Termux platform adapter for the canonical [`pleiades-factory-stack`](https://github.com/Zheke32174/pleiades-factory-stack).

It does not maintain a second tool inventory, silently clone every upstream project, or directly expose third-party execution commands. The canonical catalog remains the only source of truth.

## What the adapter does

1. Locates a checked-out canonical `pleiades-factory-stack`.
2. Reads its versioned tool catalog.
3. Selects only enabled entries carrying the `termux` profile.
4. Generates a private local adapter catalog.
5. Delegates validation, lock generation, and pinned source synchronization to the canonical toolchain.

Catalog inclusion permits source acquisition only. It does not prove that a project builds on Android, authorize execution, approve a license conclusion, or make the project a Pleiades capability.

## Prerequisites

```bash
pkg install python git

git clone https://github.com/Zheke32174/pleiades-factory-stack.git
# Until the canonical manifest-driven PR is merged, check out its review branch.

git clone https://github.com/Zheke32174/pleiades-factory-stack-termux.git
```

The repositories should be siblings, or set:

```bash
export PLEIADES_FACTORY_STACK_ROOT="$HOME/src/pleiades-factory-stack"
```

## Workflow

Preview the Termux source profile without cloning anything:

```bash
bash bootstrap-tools.sh plan
```

Resolve exact upstream commits into the private local lock:

```bash
bash bootstrap-tools.sh lock
```

Synchronize the pinned source checkouts:

```bash
bash bootstrap-tools.sh sync
```

Unpinned source acquisition requires the explicit escape hatch:

```bash
bash bootstrap-tools.sh sync --floating
```

That mode is useful for research but is not reproducible and should not feed a promoted factory artifact.

## Commands

| Command | Effect |
|---|---|
| `validate` | Validate the canonical catalog and local lock |
| `plan` | Print the selected Termux source profile |
| `lock` | Resolve exact upstream commit SHAs |
| `sync` | Clone or update only the selected pinned commits |
| `status` | Show canonical checkout, generated catalog, lock, and tools paths |

No command in this repository executes a cloned third-party project.

## State

Private generated state defaults to:

```text
~/.local/state/pleiades-factory-termux/
├── termux.catalog.json
├── termux.lock.json
└── tools-state.json
```

Source checkouts default to the `PLEIADES_TOOLS` path used by `pleiades-termux`, normally:

```text
~/.local/share/pleiades-edge/tools/
```

State and checkouts must not be committed.

## Why this replaces the previous bootstrap

The previous script carried a second hardcoded list of dozens of repositories, cloned floating default branches, swallowed failures, and reported completion based on directory count. That allowed the Android list to drift from the canonical catalog and provided no reproducible provenance.

The adapter now fails visibly when:

- the canonical checkout is absent;
- the catalog schema is wrong;
- no Termux-profile tools exist;
- a lock is missing for pinned synchronization;
- canonical synchronization detects origin, dirty-tree, or commit mismatches.

## Security boundary

- Source acquisition only; no implicit build or execution.
- Exact commit locks are the normal path.
- Generated adapter state is private.
- No API keys or credentials are handled.
- No `sudo`, systemd, containers, or root assumptions.
- No direct Pleiades authority-broker access.

## Development

```bash
python3 -m py_compile scripts/termux-adapter.py
python3 -m unittest discover -s tests -v
bash -n bootstrap-tools.sh scripts/pleiades-factory-tools.sh
```

## License

MIT — see [LICENSE](LICENSE).
