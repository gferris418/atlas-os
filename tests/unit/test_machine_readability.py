from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]


class MachineReadabilityContractTests(unittest.TestCase):
    def test_ai_entrypoint_is_schema_valid_and_points_only_to_structured_authority(self) -> None:
        schema = json.loads((ROOT / "schemas/ai-manifest.schema.json").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())

        product = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual(product["product"]["version"], manifest["product_version"])
        self.assertEqual("atlas-os.yaml", manifest["authority"]["product_manifest"])
        self.assertEqual("spec/core.yaml", manifest["authority"]["core_spec"])

        for path in manifest["machine_contracts"]:
            self.assertTrue(path.endswith((".yaml", ".yml", ".json")), path)
            self.assertTrue((ROOT / path).is_file(), path)
        for path in manifest["human_guidance"]:
            self.assertTrue(path.endswith(".md"), path)
            self.assertTrue((ROOT / path).is_file(), path)

    def test_governance_policy_is_machine_authority_and_markdown_is_companion(self) -> None:
        schema = json.loads((ROOT / "schemas/governance.schema.json").read_text(encoding="utf-8"))
        policy = yaml.safe_load((ROOT / "governance.yaml").read_text(encoding="utf-8"))
        jsonschema.validate(policy, schema, format_checker=jsonschema.FormatChecker())

        self.assertEqual("atlas-os.yaml", policy["authority"]["product_manifest"])
        self.assertEqual("atlas-ai.yaml", policy["authority"]["ai_manifest"])
        self.assertEqual("GOVERNANCE.md", policy["authority"]["human_companion"])
        self.assertEqual(
            ["DRAFT", "CANDIDATE", "VERIFIED", "RELEASED", "SUPERSEDED", "ARCHIVED"],
            policy["release"]["lifecycle"],
        )
        self.assertFalse(policy["release"]["missing_evidence_is_pass"])
        self.assertTrue(policy["migration"]["blockers_close_only_with_evidence"])

        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual("governance.yaml", manifest["authority"]["governance"])
        ai_manifest = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        self.assertIn("governance.yaml", ai_manifest["machine_contracts"])
        self.assertIn("schemas/governance.schema.json", ai_manifest["machine_contracts"])
        self.assertIn("GOVERNANCE.md", ai_manifest["human_guidance"])

    def test_release_verification_contracts_exist_for_every_supported_external_surface(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/release-verification.schema.json").read_text(encoding="utf-8")
        )
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        expected_version = manifest["product"]["version"]
        expected_surfaces = {"chatgpt", "codex", "work", "hermes-agent"}
        observed_surfaces: set[str] = set()

        for surface in sorted(expected_surfaces):
            path = ROOT / "integrations" / surface / "release-verification.yaml"
            self.assertTrue(path.is_file(), path.as_posix())
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
            jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
            self.assertEqual(surface, record["surface"])
            self.assertEqual(expected_version, record["product_version"])
            self.assertTrue(record["checks"])
            observed_surfaces.add(record["surface"])

        self.assertEqual(expected_surfaces, observed_surfaces)

    def test_surface_registry_routes_to_machine_readable_adapter_contracts(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/surface-adapter.schema.json").read_text(encoding="utf-8")
        )
        registry = yaml.safe_load((ROOT / "registries/surfaces.yaml").read_text(encoding="utf-8"))
        for item in registry["items"]:
            with self.subTest(surface=item["id"]):
                self.assertTrue(item["source"].endswith("/adapter.yaml"), item["source"])
                self.assertEqual(item["source"], item["path"])
                path = ROOT / item["source"]
                self.assertTrue(path.is_file(), path.as_posix())
                adapter = yaml.safe_load(path.read_text(encoding="utf-8"))
                jsonschema.validate(adapter, schema, format_checker=jsonschema.FormatChecker())
                self.assertEqual(item["id"], adapter["surface_id"])

    def test_migration_controls_use_structured_acceptance_and_evidence(self) -> None:
        schema = json.loads((ROOT / "schemas/migration.schema.json").read_text(encoding="utf-8"))
        for path in sorted((ROOT / "migration").glob("*.yaml")):
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
            jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
            for criterion in record["acceptance_criteria"]:
                self.assertIsInstance(criterion, dict, path.as_posix())
                self.assertTrue({"id", "requirement", "surfaces", "evidence_type"} <= set(criterion))
            for evidence in record["evidence"]:
                self.assertIsInstance(evidence, dict, path.as_posix())
                self.assertTrue(
                    {"id", "type", "timestamp", "result", "source", "independent", "scope", "limitations"}
                    <= set(evidence)
                )

    def test_migration_registry_mirrors_canonical_control_state(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/migrations.yaml").read_text(encoding="utf-8"))
        items = {item["id"]: item for item in registry["items"]}
        status_map = {
            "OPEN": "open",
            "BLOCKED": "blocked",
            "IN_PROGRESS": "in-progress",
            "CLOSED": "closed",
        }
        for path in sorted((ROOT / "migration").glob("*.yaml")):
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
            item = items[record["id"]]
            self.assertEqual(status_map[record["status"]], item["status"])
            self.assertEqual(record["release_blocking"], item["release_blocking"])
            self.assertEqual(record["dependencies"], item["dependencies"])
            self.assertEqual(path.relative_to(ROOT).as_posix(), item["source"])


if __name__ == "__main__":
    unittest.main()
