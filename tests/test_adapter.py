import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "scripts" / "termux-adapter.py"
SPEC = importlib.util.spec_from_file_location("termux_adapter", MODULE_PATH)
adapter = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(adapter)


def catalog() -> dict:
    return {
        "schema": adapter.CATALOG_SCHEMA,
        "tools": [
            {
                "name": "yes-tool",
                "url": "https://github.com/example/yes-tool.git",
                "category": "test",
                "profiles": ["termux", "all"],
                "ref": None,
                "license_hint": "MIT",
                "license_review": "required",
            },
            {
                "name": "no-tool",
                "url": "https://github.com/example/no-tool.git",
                "category": "test",
                "profiles": ["all"],
                "ref": None,
                "license_hint": "MIT",
                "license_review": "required",
            },
            {
                "name": "disabled-tool",
                "url": "https://github.com/example/disabled-tool.git",
                "category": "test",
                "profiles": ["termux"],
                "ref": None,
                "license_hint": "MIT",
                "license_review": "required",
                "enabled": False,
            },
        ],
    }


def identity(commit: str = "a" * 40) -> dict:
    return {
        "schema": adapter.SOURCE_SCHEMA,
        "repository": adapter.CANONICAL_REPOSITORY,
        "commit": commit,
        "catalog_sha256": "b" * 64,
        "toolchain_sha256": "c" * 64,
        "component_sha256": "d" * 64,
        "dirty": False,
    }


class AdapterTests(unittest.TestCase):
    def test_filters_only_termux_profile_and_binds_source(self):
        source = identity()
        filtered = adapter.filter_catalog(catalog(), source)
        self.assertEqual([tool["name"] for tool in filtered["tools"]], ["yes-tool"])
        self.assertEqual(filtered["tools"][0]["profiles"], ["core", "termux"])
        self.assertFalse(filtered["policy"]["execution_authorized"])
        self.assertEqual(
            filtered["policy"]["canonical_repository"],
            adapter.CANONICAL_REPOSITORY,
        )
        self.assertEqual(filtered["policy"]["canonical_commit"], source["commit"])
        self.assertEqual(
            filtered["policy"]["canonical_catalog_sha256"],
            source["catalog_sha256"],
        )

    def test_empty_profile_fails(self):
        with self.assertRaises(adapter.AdapterError):
            adapter.filter_catalog({"schema": adapter.CATALOG_SCHEMA, "tools": []})

    def test_wrong_schema_fails(self):
        with self.assertRaises(adapter.AdapterError):
            adapter.filter_catalog({"schema": "wrong", "tools": []})

    def test_source_pin_requires_exact_fields_and_identity(self):
        source = identity()
        adapter.validate_source_pin(dict(source), source)

        missing = dict(source)
        del missing["catalog_sha256"]
        with self.assertRaises(adapter.AdapterError):
            adapter.validate_source_pin(missing, source)

        altered = dict(source)
        altered["commit"] = "e" * 40
        with self.assertRaises(adapter.AdapterError):
            adapter.validate_source_pin(altered, source)

        dirty = dict(source)
        dirty["dirty"] = True
        with self.assertRaises(adapter.AdapterError):
            adapter.validate_source_pin(dirty, source)

    def test_canonical_identity_rejects_substituted_origin_and_reports_dirty(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "pleiades-factory-stack"
            (root / "scripts").mkdir(parents=True)
            (root / "catalog").mkdir()
            (root / "scripts" / "toolchain.py").write_text(
                "print('fixture')\n",
                encoding="utf-8",
            )
            (root / "catalog" / "tools.catalog.json").write_text(
                json.dumps(catalog()),
                encoding="utf-8",
            )
            (root / "MODOS_COMPONENT.yaml").write_text(
                "apiVersion: modos.pleiades/v1alpha1\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "fixture@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Fixture"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "remote", "add", "origin", adapter.CANONICAL_URL],
                cwd=root,
                check=True,
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)

            source = adapter.canonical_identity(root)
            self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")
            self.assertFalse(source["dirty"])
            self.assertEqual(source["repository"], adapter.CANONICAL_REPOSITORY)

            (root / "catalog" / "tools.catalog.json").write_text(
                json.dumps({"schema": "changed"}),
                encoding="utf-8",
            )
            self.assertTrue(adapter.canonical_identity(root)["dirty"])

            subprocess.run(
                ["git", "remote", "set-url", "origin", "https://github.com/example/substitute"],
                cwd=root,
                check=True,
            )
            with self.assertRaises(adapter.AdapterError):
                adapter.canonical_identity(root)

    def test_atomic_state_is_private(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "state" / "pin.json"
            adapter.atomic_json(path, identity())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema"], adapter.SOURCE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
