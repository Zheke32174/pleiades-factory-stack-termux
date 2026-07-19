# Contributing

Changes should remain narrowly scoped to canonical-source verification, Termux profile filtering, private state, delegation, documentation, tests, and reproducible source distribution.

## Rules

- Do not add a second tool catalog or hardcoded clone list.
- Do not add direct build or execution commands for cataloged projects.
- Do not weaken the canonical repository, clean-tree, commit, or digest checks.
- Keep floating acquisition explicit and outside promoted work.
- Do not commit generated state, tool checkouts, credentials, private paths, or operational evidence.
- Treat catalog inclusion as evaluation interest only.

## Required checks

```bash
python3 -m py_compile scripts/termux-adapter.py ci/scan_public_repo.py scripts/write_spdx_sbom.py
python3 -m unittest discover -s tests -v
bash -n bootstrap-tools.sh scripts/pleiades-factory-tools.sh scripts/package_source.sh
python3 ci/scan_public_repo.py
bash scripts/package_source.sh dist
(cd dist && sha256sum -c SHA256SUMS.txt)
```

Explain canonical-source, lock, state, compatibility, migration, rollback, and third-party license effects in each pull request.

Release identities are immutable. No response-time, production-support, or long-term compatibility guarantee is offered.
