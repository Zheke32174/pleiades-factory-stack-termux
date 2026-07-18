#!/usr/bin/env python3
"""Termux adapter for the canonical pleiades-factory-stack toolchain.

The adapter filters the canonical catalog to entries carrying the `termux`
profile and delegates validation, lock generation, and source synchronization
to the canonical toolchain implementation. It does not maintain a second tool
list and does not execute cloned tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import uuid
from typing import Any

CATALOG_SCHEMA = "pleiades.factory-tool-catalog/v1"
ADAPTER_SCHEMA = "pleiades.factory-termux-adapter/v1"
SOURCE_SCHEMA = "pleiades.factory-termux-source/v1"
CANONICAL_REPOSITORY = "Zheke32174/pleiades-factory-stack"
CANONICAL_URL = "https://github.com/Zheke32174/pleiades-factory-stack"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


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


def fsync_directory(path: pathlib.Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    temporary = path.with_name(
        f".{path.name}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    )
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        view = memoryview(data)
        written = 0
        while written < len(view):
            count = os.write(fd, view[written:])
            if count <= 0:
                raise AdapterError("state write made no progress")
            written += count
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        temporary.unlink(missing_ok=True)
        raise
    else:
        os.close(fd)
    os.replace(temporary, path)
    path.chmod(0o600)
    fsync_directory(path.parent)


def normalize_repo_url(value: str) -> str:
    normalized = value.strip()
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.removeprefix("git@github.com:")
    return normalized.removesuffix("/").removesuffix(".git").lower()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise AdapterError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def git_capture(root: pathlib.Path, *arguments: str) -> str:
    process = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        detail = (process.stderr or process.stdout).strip()
        raise AdapterError(
            f"canonical Git command failed ({process.returncode}): "
            f"git {' '.join(arguments)}\n{detail}"
        )
    return process.stdout.strip()


def canonical_root(adapter_root: pathlib.Path) -> pathlib.Path:
    explicit = os.environ.get("PLEIADES_FACTORY_STACK_ROOT")
    candidates: list[pathlib.Path] = []
    if explicit:
        candidates.append(pathlib.Path(explicit).expanduser())
    candidates.extend(
        [
            adapter_root.parent / "pleiades-factory-stack",
            pathlib.Path.home() / "src" / "pleiades-factory-stack",
        ]
    )
    for candidate in candidates:
        if (
            (candidate / "scripts" / "toolchain.py").is_file()
            and (candidate / "catalog" / "tools.catalog.json").is_file()
            and (candidate / "MODOS_COMPONENT.yaml").is_file()
            and (candidate / ".git").is_dir()
        ):
            return candidate.resolve()
    raise AdapterError(
        "canonical pleiades-factory-stack Git checkout not found; set "
        "PLEIADES_FACTORY_STACK_ROOT to its path"
    )


def canonical_identity(canonical: pathlib.Path) -> dict[str, Any]:
    origin = git_capture(canonical, "remote", "get-url", "origin")
    if normalize_repo_url(origin) != normalize_repo_url(CANONICAL_URL):
        raise AdapterError(
            f"canonical origin mismatch; expected {CANONICAL_URL}, found {origin}"
        )
    commit = git_capture(canonical, "rev-parse", "HEAD")
    if not SHA_RE.fullmatch(commit):
        raise AdapterError("canonical checkout did not resolve to a full commit SHA")
    dirty = bool(git_capture(canonical, "status", "--porcelain"))
    return {
        "schema": SOURCE_SCHEMA,
        "repository": CANONICAL_REPOSITORY,
        "commit": commit,
        "catalog_sha256": sha256_file(canonical / "catalog" / "tools.catalog.json"),
        "toolchain_sha256": sha256_file(canonical / "scripts" / "toolchain.py"),
        "component_sha256": sha256_file(canonical / "MODOS_COMPONENT.yaml"),
        "dirty": dirty,
    }


def validate_source_pin(pin: dict[str, Any], identity: dict[str, Any]) -> None:
    expected_keys = {
        "schema",
        "repository",
        "commit",
        "catalog_sha256",
        "toolchain_sha256",
        "component_sha256",
        "dirty",
    }
    if set(pin) != expected_keys:
        raise AdapterError("canonical source pin has unknown or missing fields")
    if pin.get("schema") != SOURCE_SCHEMA:
        raise AdapterError(f"canonical source pin schema must be {SOURCE_SCHEMA}")
    if pin.get("dirty") is not False:
        raise AdapterError("canonical source pin must describe a clean checkout")
    for key in (
        "repository",
        "commit",
        "catalog_sha256",
        "toolchain_sha256",
        "component_sha256",
    ):
        if pin.get(key) != identity.get(key):
            raise AdapterError(f"canonical source pin mismatch: {key}")


def filter_catalog(
    catalog: dict[str, Any],
    identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
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
        tool["profiles"] = ["core", "termux"]
        selected.append(tool)

    if not selected:
        raise AdapterError("canonical catalog contains no enabled termux-profile tools")

    policy: dict[str, Any] = {
        "description": (
            "Generated Termux source-only view of the canonical Pleiades "
            "factory catalog."
        ),
        "generated_by": ADAPTER_SCHEMA,
        "default_profile": "core",
        "source_only": True,
        "execution_authorized": False,
    }
    if identity is not None:
        policy["canonical_repository"] = identity["repository"]
        policy["canonical_commit"] = identity["commit"]
        policy["canonical_catalog_sha256"] = identity["catalog_sha256"]
        policy["canonical_toolchain_sha256"] = identity["toolchain_sha256"]
        policy["canonical_component_sha256"] = identity["component_sha256"]

    return {
        "schema": CATALOG_SCHEMA,
        "policy": policy,
        "tools": selected,
    }


def run_toolchain(
    canonical: pathlib.Path,
    generated_catalog: pathlib.Path,
    lock_path: pathlib.Path,
    command: list[str],
) -> int:
    toolchain = canonical / "scripts" / "toolchain.py"
    process = subprocess.run(
        [
            sys.executable,
            str(toolchain),
            "--catalog",
            str(generated_catalog),
            "--lock",
            str(lock_path),
            *command,
        ],
        check=False,
    )
    return process.returncode


def main() -> int:
    adapter_root = pathlib.Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["validate", "plan", "pin", "lock", "sync", "status"],
    )
    parser.add_argument("extra", nargs=argparse.REMAINDER)
    parser.add_argument(
        "--state-root",
        type=pathlib.Path,
        default=pathlib.Path(
            os.environ.get(
                "PLEIADES_FACTORY_TERMUX_STATE",
                pathlib.Path.home()
                / ".local"
                / "state"
                / "pleiades-factory-termux",
            )
        ),
    )
    args = parser.parse_args()

    try:
        canonical = canonical_root(adapter_root)
        identity = canonical_identity(canonical)
        state_root = args.state_root.expanduser()
        state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            state_root.chmod(0o700)
        except OSError:
            pass
        generated_catalog = state_root / "termux.catalog.json"
        source_pin = state_root / "canonical-source.json"
        lock_path = pathlib.Path(
            os.environ.get(
                "PLEIADES_FACTORY_TERMUX_LOCK",
                state_root / "termux.lock.json",
            )
        ).expanduser()
        tools_dir = pathlib.Path(
            os.environ.get(
                "PLEIADES_TOOLS",
                pathlib.Path.home()
                / ".local"
                / "share"
                / "pleiades-edge"
                / "tools",
            )
        ).expanduser()
        sync_state = state_root / "tools-state.json"

        catalog = filter_catalog(
            load_json(canonical / "catalog" / "tools.catalog.json"),
            identity,
        )

        if args.command == "status":
            pin_matches = False
            pin_error = None
            if source_pin.is_file():
                try:
                    validate_source_pin(load_json(source_pin), identity)
                    pin_matches = True
                except AdapterError as exc:
                    pin_error = str(exc)
            value = {
                "schema": ADAPTER_SCHEMA,
                "canonical_root": str(canonical),
                "canonical_identity": identity,
                "canonical_source_pin": str(source_pin),
                "source_pin_present": source_pin.is_file(),
                "source_pin_matches": pin_matches,
                "source_pin_error": pin_error,
                "generated_catalog": str(generated_catalog),
                "lock": str(lock_path),
                "lock_present": lock_path.is_file(),
                "tools_dir": str(tools_dir),
                "selected_tools": [tool["name"] for tool in catalog["tools"]],
                "execution_authorized": False,
            }
            print(json.dumps(value, indent=2, sort_keys=True))
            return 0

        if identity["dirty"]:
            raise AdapterError(
                "canonical factory-stack checkout is dirty; commit or discard "
                "changes before generating adapter state"
            )

        if args.command == "pin":
            atomic_json(source_pin, identity)
            print(json.dumps(identity, indent=2, sort_keys=True))
            return 0

        if args.command in {"lock", "sync"}:
            if not source_pin.is_file():
                raise AdapterError(
                    "canonical source is not pinned; run the pin command after review"
                )
            validate_source_pin(load_json(source_pin), identity)

        atomic_json(generated_catalog, catalog)
        command = [args.command]
        if args.command == "sync":
            command.extend(
                ["--tools-dir", str(tools_dir), "--state", str(sync_state)]
            )
        command.extend(args.extra)
        return run_toolchain(canonical, generated_catalog, lock_path, command)
    except AdapterError as exc:
        print(f"pleiades-factory-termux: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
