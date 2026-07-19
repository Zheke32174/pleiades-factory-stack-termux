# Changelog

## Unreleased

- Verify the first immutable `v0.2.0` GitHub Release assets after stacked review and integration.

## 0.2.0

- replace the duplicate floating tool list with a thin canonical Termux adapter;
- verify exact canonical repository, clean state, commit, catalog, toolchain, and component-declaration identities;
- keep canonical-source and selected-upstream lock layers separate;
- delegate validation, locking, and source synchronization to the canonical toolchain;
- remove direct third-party execution commands;
- add private atomic state, tests, status reporting, and refusal behavior;
- add the previously missing MIT license;
- replace mutable branch-triggered showcase releases and false GHCR claims with immutable source releases;
- add deterministic source packaging, checksums, SPDX inventory, and exact-commit receipts;
- add current-tree and reachable-history sensitivity scanning;
- add security, privacy, contribution, update, rollback, removal, and support documentation;
- restrict feature-branch validation to one pull-request workflow.

`0.2.0` is not published until the reviewed tag creates and verifies the named source assets.

## Historical state

Earlier revisions maintained a separate hardcoded project list and direct execution helpers, which could drift from the canonical catalog. Historical `v0.1.0` identity must not be overwritten to represent the verified adapter release.
