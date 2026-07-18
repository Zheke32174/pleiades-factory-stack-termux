# Pleiades Factory Stack — Termux Adapter

This repository is the Android/Termux platform adapter for the canonical [`pleiades-factory-stack`](https://github.com/Zheke32174/pleiades-factory-stack).

It does not maintain a second tool inventory, silently clone every upstream project, or directly expose third-party execution commands. The canonical catalog remains the only source of truth.

## What the adapter does

1. Locates a Git checkout of the canonical `pleiades-factory-stack` repository.
2. Verifies its exact origin, commit, clean working-tree state, catalog hash, toolchain hash, and component-contract hash.
3. Reads its versioned tool catalog.
4. Selects only enabled entries carrying the `termux` profile.
5. Generates a private local adapter catalog bound to that canonical source identity.
6. Delegates validation, lock generation, and pinned source synchronization to the canonical toolchain.

Catalog inclusion permits source acquisition only. It does not prove that a project builds on Android, authorize execution, approve a license conclusion, or make the project a Pleiades capability.

## Two independent lock layers

The adapter distinguishes two kinds of provenance:

- `canonical-source.json` pins the exact reviewed `pleiades-factory-stack` commit and the SHA-256 hashes of its catalog, toolchain, and component declaration.
- `termux.lock.json` pins the selected third-party projects to exact upstream commits.

A reviewed upstream-tool lock cannot compensate for a substituted or dirty canonical catalog. Conversely, pinning the factory-stack source does not approve or execute any listed third-party project.

## Prerequisites

```bash
pkg install python git

git clone https://github.com/Zheke32174/pleiades-factory-stack.git
git clone https://github.com/Zheke32174/pleiades-factory-stack-termux.git
```

The repositories should be siblings, or set:

```bash
export PLEIADES_FACTORY_STACK_ROOT="$HOME/src/pleiades-factory-stack"
```

The canonical checkout must have the exact `Zheke32174/pleiades-factory-stack` origin and a clean working tree before adapter state can be generated.

## Workflow

Preview the clean canonical Termux source profile without cloning anything:

```bash
bash bootstrap-tools.sh plan
```

After reviewing the canonical commit and reported hashes, pin that source identity:

```bash
bash bootstrap-tools.sh pin
```

Resolve exact upstream commits into the private local tool lock:

```bash
bash bootstrap-tools.sh lock
```

Synchronize the pinned source checkouts:

```bash
bash bootstrap-tools.sh sync
```

Unpinned upstream source acquisition remains an explicit research escape hatch:

```bash
bash bootstrap-tools.sh sync --floating
```

That flag does **not** bypass the canonical factory-source pin. It changes only the selected upstream-project lock requirement and should not feed a promoted factory artifact.

## Commands

| Command | Effect |
|---|---|
| `validate` | Validate the clean canonical catalog and any local tool lock |
| `plan` | Print the selected Termux source profile |
| `pin` | Record the exact clean canonical repository commit and content hashes |
| `lock` | Resolve exact upstream commit SHAs; requires a matching source pin |
| `sync` | Clone or update selected sources; requires a matching source pin |
| `status` | Non-mutating report of source identity, pin match, locks, paths, and tools |

No command in this repository executes a cloned third-party project.

## State

Private generated state defaults to:

```text
~/.local/state/pleiades-factory-termux/
├── canonical-source.json
├── termux.catalog.json
├── termux.lock.json
└── tools-state.json
```

Source checkouts default to the `PLEIADES_TOOLS` path used by `pleiades-termux`, normally:

```text
~/.local/share/pleiades-edge/tools/
```

State and checkouts must not be committed.

## Refusal behavior

The adapter fails visibly when:

- the canonical Git checkout is absent;
- its origin is not `Zheke32174/pleiades-factory-stack`;
- its working tree is dirty;
- its catalog schema is wrong;
- no enabled Termux-profile tools exist;
- the canonical-source pin is missing or no longer matches;
- an upstream lock is missing for pinned synchronization;
- canonical synchronization detects origin, dirty-tree, or commit mismatches.

`status` is deliberately non-mutating and can report a dirty checkout or stale/missing source pin without rewriting generated state.

## Security boundary

- Source acquisition only; no implicit build or execution.
- Exact canonical-source and upstream-tool identities are separate normal-path gates.
- Generated adapter state is private and atomically replaced.
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
