# Pleiades Factory Stack Termux

Termux-adapted sister repo of [pleiades-factory-stack](https://github.com/Zheke32174/pleiades-factory-stack). Bootstraps a research toolchain for binary analysis, cross-ISA emulation, and AI/LLM agent integration — adapted for Android/Termux.

## What's Here

| File | Purpose |
|------|---------|
| `bootstrap-tools.sh` | Clones all third-party tools into `$PLEIADES_TOOLS` |
| `scripts/pleiades-factory-tools.sh` | CLI wrapper for factory tools |

## Quick Start

```bash
# Source environment
source pleiades-termux/env/pleiades-env.sh

# Clone all tools
bash bootstrap-tools.sh

# List available tools
bash scripts/pleiades-factory-tools.sh list
```

## Termux Adaptation

- Tools directory defaults to `$PLEIADES_TOOLS` (not `./tools/`)
- Compatibility layer handles path mappings and stub commands
- Failed clones are skipped with a warning (some tools may not compile on aarch64/Android)

## Related Repos

| Repo | Purpose |
|------|---------|
| [pleiades-termux](https://github.com/Zheke32174/pleiades-termux) | Host scripts, agent suite, env config |
| [pleiades-container-termux](https://github.com/Zheke32174/pleiades-container-termux) | Container bootstrap (reference) |
| *this repo* | Toolchain bootstrap |
