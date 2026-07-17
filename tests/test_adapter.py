import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "scripts" / "termux-adapter.py"
SPEC = importlib.util.spec_from_file_location("termux_adapter", MODULE_PATH)
adapter = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(adapter)


class AdapterTests(unittest.TestCase):
    def test_filters_only_termux_profile(self):
        catalog = {
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
        filtered = adapter.filter_catalog(catalog)
        self.assertEqual([tool["name"] for tool in filtered["tools"]], ["yes-tool"])
        self.assertEqual(filtered["tools"][0]["profiles"], ["core", "termux"])
        self.assertFalse(filtered["policy"]["execution_authorized"])

    def test_empty_profile_fails(self):
        with self.assertRaises(adapter.AdapterError):
            adapter.filter_catalog({"schema": adapter.CATALOG_SCHEMA, "tools": []})

    def test_wrong_schema_fails(self):
        with self.assertRaises(adapter.AdapterError):
            adapter.filter_catalog({"schema": "wrong", "tools": []})


if __name__ == "__main__":
    unittest.main()
