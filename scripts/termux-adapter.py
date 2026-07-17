#!/usr/bin/env python3
"""Termux adapter for the canonical pleiades-factory-stack toolchain.

The adapter filters the canonical catalog to entries carrying the `termux`
profile and delegates validation, lock generation, and source synchronization
to the canonical toolchain implementation. It does not maintain a second tool
list and does not execute cloned tools.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

CATALOG_SCHEMA = "pleiades.factory-tool-catalog/v1"
ADAPTER_SCHEMA = "pleiades.factory-termux-adapter/v1"


class AdapterError(RuntimeError):
    pass


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdapterError(f"{path} must contain a JSON object")
    return value


def atomic_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def canonical_root(adapter_root: pathlib.Path) -> pathlib.Path:
    explicit = os.environ.get("PLEIADES_FACTORY_STACK_ROOT")
    candidates = []
    if explicit:
        candidates.append(pathlib.Path(explicit).expanduser())
    candidates.extend(
        [
            adapter_root.parent / "pleiades-factory-stack",
            pathlib.Path.home() / "src" / "pleiades-factory-stack",
        ]
    )
    for candidate in candidates:
        if (candidate / "scripts" / "toolchain.py").is_file() and (candidate / "catalog" / "tools.catalog.json").is_file():
            return candidate.resolve()
    raise AdapterError(
        "canonical pleiades-factory-stack checkout not found; set "
        "PLEIADES_FACTORY_STACK_ROOT to its path"
    )


def filter_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise AdapterError(f"canonical catalog schema must be {CATALOG_SCHEMA}")
    tools = catalog.get("tools")
    if not isinstance(tools, list):
        raise AdapterError("canonical catalog tools must be an array")

    selected = []
    for raw in tools:
        if not isinstance(raw, dict):
            raise AdapterError("canonical catalog contains a non-object tool")
        profiles = raw.get("profiles")
        if not isinstance(profiles, list):
            raise AdapterError(f"{raw.get('name', '?')}: profiles must be an array")
        if "termux" not in profiles or raw.get("enabled", True) is False:
            continue
        tool = dict(raw)
        # The generated catalog is consumed with the canonical CLI's default
        # `core` profile. This rewrites only the generated adapter view; the
        # canonical catalog remains the source of truth.
        tool["profiles"] = ["core", "termux"]
        selected.append(tool)

    if not selected:
        raise AdapterError("canonical catalog contains no enabled termux-profile tools")

    return {
        "schema": CATALOG_SCHEMA,
        "policy": {
            "description": "Generated Termux source-only view of the canonical Pleiades factory catalog.",
            "generated_by": ADAPTER_SCHEMA,
            "default_profile": "core",
            "source_only": True,
            "execution_authorized": False,
        },
        "tools": selected,
    }


def run_toolchain(canonical: pathlib.Path, generated_catalog: pathlib.Path, lock_path: pathlib.Path, command: list[str]) -> int:
    toolchain = canonical / "scripts" / "toolchain.py"
    process = subprocess.run(
        [sys.executable, str(toolchain), "--catalog", str(generated_catalog), "--lock", str(lock_path), *command],
        check=False,
    )
    return process.returncode


def main() -> int:
    adapter_root = pathlib.Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "plan", "lock", "sync", "status"])
    parser.add_argument("extra", nargs=argparse.REMAINDER)
    parser.add_argument(
        "--state-root",
        type=pathlib.Path,
        default=pathlib.Path(os.environ.get("PLEIADES_FACTORY_TERMUX_STATE", pathlib.Path.home() / ".local" / "state" / "pleiades-factory-termux")),
    )
    args = parser.parse_args()

    try:
        canonical = canonical_root(adapter_root)
        state_root = args.state_root.expanduser()
        state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        generated_catalog = state_root / "termux.catalog.json"
        lock_path = pathlib.Path(os.environ.get("PLEIADES_FACTORY_TERMUX_LOCK", state_root / "termux.lock.json")).expanduser()
        tools_dir = pathlib.Path(os.environ.get("PLEIADES_TOOLS", pathlib.Path.home() / ".local" / "share" / "pleiades-edge" / "tools")).expanduser()
        sync_state = state_root / "tools-state.json"

        catalog = filter_catalog(load_json(canonical / "catalog" / "tools.catalog.json"))
        atomic_json(generated_catalog, catalog)

        if args.command == "status":
            value = {
                "schema": ADAPTER_SCHEMA,
                "canonical_root": str(canonical),
                "generated_catalog": str(generated_catalog),
                "lock": str(lock_path),
                "lock_present": lock_path.is_file(),
                "tools_dir": str(tools_dir),
                "selected_tools": [tool["name"] for tool in catalog["tools"]],
                "execution_authorized": False,
            }
            print(json.dumps(value, indent=2, sort_keys=True))
            return 0

        command = [args.command]
        if args.command == "sync":
            command.extend(["--tools-dir", str(tools_dir), "--state", str(sync_state)])
        command.extend(args.extra)
        return run_toolchain(canonical, generated_catalog, lock_path, command)
    except AdapterError as exc:
        print(f"pleiades-factory-termux: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
