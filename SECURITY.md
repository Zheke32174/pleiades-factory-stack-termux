# Security Policy

## Project status

This repository is an experimental Android/Termux adapter over the canonical public `pleiades-factory-stack`. It does not maintain an independent tool inventory, execute cataloged projects, approve licenses, or grant Pleiades capability authority.

Only the current reviewed default branch and most recent verified source release are eligible for fixes.

## Report vulnerabilities privately

Use GitHub's private vulnerability-reporting or Security Advisory interface when available. Do not post credentials, private topology, local state files, cloned source, or personal data in public issues.

A useful report includes the affected commit, canonical factory-stack commit, command, expected and observed behavior, and a synthetic reproducer.

## Trust boundaries

The adapter must:

- accept only the canonical `Zheke32174/pleiades-factory-stack` repository identity;
- require a clean canonical checkout;
- separately pin the canonical source and selected third-party commits;
- verify catalog, toolchain, and component-declaration hashes;
- keep generated state private and replace it atomically;
- delegate validation, lock, and sync behavior to the canonical toolchain;
- expose no direct execution command;
- keep floating source acquisition explicit and unsuitable for promotion;
- publish only source artifacts that contain no catalog checkout, third-party source, credentials, or runtime state.

Catalog membership and source synchronization do not establish safety, Android compatibility, license approval, build success, or execution authorization.

## Local state

Generated state and cloned sources can reveal selected projects, paths, commits, failure messages, and operator choices. They must not be committed or attached publicly without review.

A stale or substituted canonical checkout must fail rather than silently regenerating trusted-looking state.

## Sensitive information

Do not commit API keys, tokens, passwords, cookies, private keys, `.env` data, private endpoints, local usernames, event evidence, or generated adapter state.

CI scans the current tracked tree and reachable Git history for configured credential, private-topology, and host-local patterns. A pass is evidence for those configured patterns, not proof of universal absence. Revoke or rotate any real secret before history remediation.

## Release integrity

A valid release must originate from `v$(cat VERSION)`, pass adapter tests and history scanning, build twice byte-for-byte, include checksums/SPDX/build receipt, and refuse release identity overwrite.
