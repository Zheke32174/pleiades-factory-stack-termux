# Pleiades Factory Stack — Termux Adapter

> **Status:** experimental but working thin source-acquisition adapter. It does not contain the canonical catalog, execute third-party projects, or grant Pleiades capability authority.

This repository adapts the canonical public [`pleiades-factory-stack`](https://github.com/Zheke32174/pleiades-factory-stack) for Android/Termux. The canonical catalog remains the only tool inventory and policy source.

## Download

Open the [GitHub Releases page](https://github.com/Zheke32174/pleiades-factory-stack-termux/releases) and download:

`pleiades-factory-stack-termux-<version>.tar.gz`

A proper release also contains `SHA256SUMS.txt`, an SPDX 2.3 JSON source inventory, and an exact-commit build receipt.

The archive contains this adapter source only. It does not contain the canonical factory checkout, canonical catalog, third-party repositories, generated state, credentials, or executable tool payloads.

Until the first verified asset-bearing tag is published, use a reviewed checkout.

## Prerequisites and install

Inside Termux:

```bash
pkg install python git

git clone https://github.com/Zheke32174/pleiades-factory-stack.git
git clone https://github.com/Zheke32174/pleiades-factory-stack-termux.git
cd pleiades-factory-stack-termux
```

Keep the repositories as siblings, or set:

```bash
export PLEIADES_FACTORY_STACK_ROOT="$HOME/src/pleiades-factory-stack"
```

The canonical checkout must have the exact `Zheke32174/pleiades-factory-stack` origin and a clean working tree.

## What the adapter does

1. Locates the canonical factory-stack checkout.
2. Verifies its origin, exact commit, clean state, catalog hash, toolchain hash, and component-declaration hash.
3. Selects only enabled catalog entries carrying the `termux` profile.
4. Generates a private local adapter catalog bound to that canonical identity.
5. Delegates validation, lock generation, and pinned source synchronization to the canonical toolchain.

Catalog inclusion permits source evaluation only. It does not prove Android compatibility, authorize execution, approve a license conclusion, or create a Pleiades capability.

## Two independent lock layers

- `canonical-source.json` pins the reviewed canonical repository commit and its catalog, toolchain, and component-declaration digests.
- `termux.lock.json` pins selected third-party repositories to exact commits.

A reviewed upstream lock cannot compensate for a substituted or dirty canonical catalog. Pinning the canonical source does not approve or execute any listed project.

## Workflow

Preview without cloning third-party source:

```bash
bash bootstrap-tools.sh plan
```

Pin the reviewed canonical source:

```bash
bash bootstrap-tools.sh pin
```

Resolve exact selected upstream commits:

```bash
bash bootstrap-tools.sh lock
```

Synchronize pinned source checkouts:

```bash
bash bootstrap-tools.sh sync
```

Exploratory floating acquisition is explicit:

```bash
bash bootstrap-tools.sh sync --floating
```

Floating mode does not bypass the canonical-source pin and must not feed promoted work.

## Commands

| Command | Effect |
|---|---|
| `validate` | Validate canonical source and any local upstream lock |
| `plan` | Print the selected Termux source profile |
| `pin` | Record the exact clean canonical source identity |
| `lock` | Resolve exact selected upstream commits |
| `sync` | Clone or update selected source checkouts |
| `status` | Non-mutating identity, pin, lock, path, and tool report |

No command in this repository builds or executes a cloned third-party project.

## State and privacy

Generated private state defaults to:

```text
~/.local/state/pleiades-factory-termux/
├── canonical-source.json
├── termux.catalog.json
├── termux.lock.json
└── tools-state.json
```

Source checkouts normally use the `PLEIADES_TOOLS` path shared with `pleiades-termux`, commonly `~/.local/share/pleiades-edge/tools/`.

State and checkouts may reveal selected projects, commits, local paths, and failures. Do not commit or publish them without review. See [PRIVACY.md](PRIVACY.md).

## Removal

Delete adapter state:

```bash
rm -rf -- "$HOME/.local/state/pleiades-factory-termux"
```

Delete this checkout separately. Remove third-party checkouts only after verifying the configured `PLEIADES_TOOLS` path. This adapter does not install a daemon, Android package, global command override, credential, or service.

## Refusal behavior

The adapter fails visibly when the canonical checkout is absent, substituted, dirty, malformed, unpinned, or stale; when no enabled Termux-profile tools exist; when pinned synchronization lacks an upstream lock; or when canonical synchronization detects origin, tree, or commit drift.

`status` remains non-mutating and can report a dirty checkout or stale/missing pin without rewriting state.

## Security boundary

- Source acquisition only; no implicit build or execution.
- Exact canonical-source and upstream-tool identities are separate gates.
- Generated adapter state is private and atomically replaced.
- No API keys, root, sudo, systemd, containers, or direct authority-broker access.
- Release assets contain adapter source only.

See [SECURITY.md](SECURITY.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Development

```bash
python3 -m py_compile scripts/termux-adapter.py ci/scan_public_repo.py scripts/write_spdx_sbom.py
python3 -m unittest discover -s tests -v
bash -n bootstrap-tools.sh scripts/pleiades-factory-tools.sh scripts/package_source.sh
python3 ci/scan_public_repo.py
bash scripts/package_source.sh dist
(cd dist && sha256sum -c SHA256SUMS.txt)
```

CI builds the source package twice and requires byte-identical output.

## Update and rollback

Update by moving both this adapter and the canonical factory stack to reviewed commits, then inspect `status` and refresh the canonical pin deliberately. A changed canonical commit or digest must not be accepted silently.

Rollback by restoring the previous reviewed adapter and canonical factory-stack commits plus their matching private pin/lock files. Preserve or remove synchronized third-party sources separately.

## License and support

MIT — see [LICENSE](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

This is a small experimental project. No response-time, production-support, Android-version, Termux-distribution, or long-term compatibility guarantee is offered.
