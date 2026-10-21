from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative: str):
    return yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))


class MachineReadableAIReadinessTests(unittest.TestCase):
    def test_ai_manifest_is_schema_valid_and_bound_from_product_authority(self) -> None:
        product = load_yaml("atlas-os.yaml")
        self.assertEqual("ai/manifest.yaml", product["authority"].get("ai_manifest"))

        schema_path = ROOT / "schemas/ai-manifest.schema.json"
        manifest_path = ROOT / "ai/manifest.yaml"
        self.assertTrue(schema_path.is_file())
        self.assertTrue(manifest_path.is_file())

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        manifest = load_yaml("ai/manifest.yaml")
        jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())
        self.assertEqual(product["product"]["version"], manifest["product"]["version"])
        self.assertEqual("atlas-os.yaml", manifest["product"]["authority"])
        self.assertEqual(["yaml", "json"], manifest["policy"]["authoritative_formats"])
        self.assertEqual("documentation-only", manifest["policy"]["markdown_role"])

    def test_every_active_surface_uses_a_machine_readable_adapter_authority(self) -> None:
        schema_path = ROOT / "schemas/ai-host-adapter.schema.json"
        self.assertTrue(schema_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        surfaces = load_yaml("registries/surfaces.yaml")

        for surface in surfaces["items"]:
            if surface["status"] != "active":
                continue
            with self.subTest(surface=surface["id"]):
                self.assertTrue(surface["source"].endswith((".yaml", ".json")))
                self.assertEqual(surface["source"], surface["path"])
                adapter_path = ROOT / surface["source"]
                self.assertTrue(adapter_path.is_file())
                adapter = load_yaml(surface["source"])
                jsonschema.validate(adapter, schema, format_checker=jsonschema.FormatChecker())
                self.assertEqual(surface["id"], adapter["surface_id"])
                self.assertEqual("atlas-os.yaml", adapter["authority"]["product_manifest"])

    def test_every_active_output_profile_is_canonically_machine_readable(self) -> None:
        registry = load_yaml("registries/output-profiles.yaml")
        for profile in registry["items"]:
            if profile["status"] != "active":
                continue
            with self.subTest(profile=profile["id"]):
                self.assertIs(profile["machine_readable"], True)
                self.assertIn(profile["format"], {"json", "yaml"})
                self.assertIn(profile["format"], profile["supported_formats"])
                self.assertIn(profile["format"], profile["file_extensions"])

    def test_external_release_verification_is_machine_readable(self) -> None:
        schema_path = ROOT / "schemas/release-verification.schema.json"
        self.assertTrue(schema_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        expected = {
            "surface.chatgpt": "integrations/chatgpt/release-verification.yaml",
            "surface.work": "integrations/work/release-verification.yaml",
            "surface.codex": "integrations/codex/release-verification.yaml",
            "surface.hermes-agent": "integrations/hermes-agent/release-verification.yaml",
        }
        for surface_id, relative in expected.items():
            with self.subTest(surface=surface_id):
                self.assertTrue((ROOT / relative).is_file())
                record = load_yaml(relative)
                jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
                self.assertEqual(surface_id, record["surface_id"])
                self.assertEqual("PENDING_EXTERNAL_EVIDENCE", record["status"])

    def test_migration_registry_status_matches_canonical_migration_records(self) -> None:
        registry = load_yaml("registries/migrations.yaml")
        by_id = {item["id"]: item for item in registry["items"]}
        for relative in ("migration/MIG-029.yaml", "migration/MIG-037.yaml"):
            record = load_yaml(relative)
            with self.subTest(migration=record["id"]):
                self.assertIn(record["id"], by_id)
                self.assertEqual(record["status"].lower(), by_id[record["id"]]["status"])
                self.assertEqual(record["release_blocking"], by_id[record["id"]]["release_blocking"])


if __name__ == "__main__":
    unittest.main()
