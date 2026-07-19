# Third-Party Notices

Pleiades-owned adapter source in this repository is MIT licensed.

This repository does not bundle the canonical `pleiades-factory-stack` checkout, its generated lock, cataloged third-party repositories, or executed third-party tools in its source releases.

## Canonical Pleiades Factory Stack

The adapter requires a separate reviewed checkout of:

`https://github.com/Zheke32174/pleiades-factory-stack`

That repository retains its own license, notices, release identity, catalog policy, and security boundary. This adapter records its exact commit and content digests but does not copy its catalog into the versioned adapter release.

## Cataloged third-party projects

When the operator runs `lock` or `sync`, the canonical toolchain can resolve or clone selected upstream repositories. Those projects remain governed by their own licenses, notices, trademarks, dependencies, platform rules, and acceptable-use restrictions.

Catalog inclusion, exact pinning, or successful source synchronization does not authorize:

- execution;
- installation;
- modification;
- redistribution;
- embedding in an Android package or image;
- exposure as a network service;
- treatment as a promoted Pleiades capability.

Review the exact locked revision before any build, integration, redistribution, or deployment.

## Termux, Android, Python, and Git

Termux, Android, Python, Git, the device operating system, package manager, and shared storage are not bundled here. Their licenses, privacy behavior, platform policies, update channels, and security support apply independently.

## GitHub Actions

Repository workflows use GitHub Actions such as `actions/checkout` and `actions/upload-artifact`. Their licenses and hosted-execution terms apply independently. Workflow invocation does not make them part of the MIT-licensed adapter runtime.

## Downstream obligations

A downstream package, bundled canonical checkout, redistributed third-party source tree, generated Android artifact, or hosted service can create additional license, notice, corresponding-source, privacy, trademark, and platform-policy obligations. Review the actual downstream artifact and deployment model rather than relying on this notice as a legal conclusion.
