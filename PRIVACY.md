# Privacy and Data Behavior

This adapter includes no analytics, advertising, account tracking, or hosted service.

## Local data

Generated state defaults to `~/.local/state/pleiades-factory-termux/` and can include:

- the exact canonical factory-stack repository identity and commit;
- hashes of the canonical catalog, toolchain, and component declaration;
- the generated Termux-profile catalog;
- selected third-party lock entries;
- synchronization results, local paths, and failure messages.

Third-party source checkouts normally live under the Pleiades Termux tools directory. They remain governed by their upstream projects and can contain their own metadata, history, or generated files.

## Network behavior

`status`, local validation, tests, sensitivity scanning, and source-package generation do not contact a Pleiades service.

`lock` and `sync` delegate to the canonical public factory toolchain and can contact the Git hosts named in the selected catalog entries. Those hosts can observe ordinary connection metadata and apply their own privacy policies.

This adapter does not upload its state, credentials, event data, or diagnostics to a maintainer endpoint.

## Retention and deletion

State and synchronized source remain until the operator removes them. To remove adapter state:

```bash
rm -rf -- "$HOME/.local/state/pleiades-factory-termux"
```

Remove cloned third-party source only after verifying the configured `PLEIADES_TOOLS` path. Deleting this adapter checkout does not automatically delete canonical factory state or third-party source checkouts.

## Public collaboration

Do not attach real `canonical-source.json`, lock files, state receipts, local paths, private repository references, or cloned source to public issues without review and redaction. Use synthetic fixtures.
