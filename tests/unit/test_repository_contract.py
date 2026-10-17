from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema
import yaml

from atlas_runtime import create_dashboard, select_output_profile, validate_output_record


ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_manifest_is_only_product_version_authority(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual("2.0.0-rc.4", manifest["product"]["version"])
        self.assertEqual("atlas-os.yaml#/product/version", (ROOT / "VERSION").read_text().strip())

    def test_closed_migration_requires_evidence(self) -> None:
        schema = json.loads((ROOT / "schemas/migration.schema.json").read_text())
        record = yaml.safe_load((ROOT / "migration/MIG-029.yaml").read_text())
        record["status"] = "CLOSED"
        record["closed_at"] = "2026-10-17T20:00:00+06:00"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())

    def test_repository_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/validate/validate_repository.py", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_compact_dashboard_matches_its_schema(self) -> None:
        schema = json.loads((ROOT / "schemas/dashboard.schema.json").read_text())
        dashboard = create_dashboard(
            "Verify contract", progress=50, active_unit="validate", completed_units=1, total_units=2,
        )
        jsonschema.validate(dashboard, schema)

    def test_output_profile_registry_and_sample_envelope_agree(self) -> None:
        schema = json.loads((ROOT / "schemas/output.schema.json").read_text())
        sample = json.loads((ROOT / "tests/fixtures/sample-output.json").read_text())
        registry = yaml.safe_load((ROOT / "registries/output-profiles.yaml").read_text())
        jsonschema.validate(sample, schema, format_checker=jsonschema.FormatChecker())
        profile = select_output_profile(
            ["DECISION"], registry["items"], requested_id=sample["profile"]
        )
        self.assertTrue(validate_output_record(sample, profile)["valid"])

    def test_structured_l2_tasks_require_domain_classification_and_alignment(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        task["execution_depth"] = "L2"
        jsonschema.validate(task, schema)
        task.pop("domain_classification")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(task, schema)
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        task["execution_depth"] = "L2"
        task.pop("domain_alignment")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(task, schema)

    def test_l1_task_may_omit_explicit_domain_classification_and_alignment(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        task.pop("domain_classification")
        task.pop("domain_alignment")
        jsonschema.validate(task, schema)

    def test_bangladesh_navy_radar_workflow_example_is_schema_valid(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        example = json.loads(
            (ROOT / "examples/workflows/coastal-surveillance-radar-bangladesh-navy.json")
            .read_text(encoding="utf-8")
        )
        jsonschema.validate(example, schema)
        self.assertEqual("PARTIAL", example["domain_classification"]["status"])
        self.assertEqual("BLOCKED", example["status"])
        self.assertIn("lifecycle-stage", example["domain_classification"]["unresolved_facets"])
        self.assertIn("information-sensitivity", example["domain_classification"]["unresolved_facets"])


if __name__ == "__main__":
    unittest.main()

