from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

import jsonschema
import yaml

from atlas_runtime import (
    create_dashboard,
    prepare_library_record,
    select_output_profile,
    validate_output_record,
)
from tools.package.build_release import validate_release_tag

ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_manifest_is_only_product_version_authority(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual("2.0.1", manifest["product"]["version"])
        self.assertEqual("atlas-os.yaml#/product/version", (ROOT / "VERSION").read_text().strip())

    def test_manifest_declares_the_repository_license_separately_from_classification(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual("internal", manifest["product"]["classification"])
        self.assertEqual("MIT", manifest["product"]["license"])
        self.assertTrue((ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"))

    def test_release_tag_must_match_manifest_and_release_state(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        version = manifest["product"]["version"]
        self.assertEqual(f"v{version}", validate_release_tag(manifest, f"v{version}", []))
        with self.assertRaisesRegex(RuntimeError, "does not match"):
            validate_release_tag(manifest, "v2.0.0", [])

        stable = deepcopy(manifest)
        stable["product"].update({
            "version": "2.0.1",
            "release_channel": "stable",
            "status": "RELEASED",
        })
        stable["release"]["target_version"] = "2.0.1"
        with self.assertRaisesRegex(RuntimeError, "open release blockers"):
            validate_release_tag(stable, "v2.0.1", ["MIG-029"])
        self.assertEqual("v2.0.1", validate_release_tag(stable, "v2.0.1", []))

    def test_closed_migration_requires_evidence(self) -> None:
        schema = json.loads((ROOT / "schemas/migration.schema.json").read_text())
        record = yaml.safe_load((ROOT / "migration/MIG-029.yaml").read_text())
        record["status"] = "CLOSED"
        record["closed_at"] = "2026-10-17T20:00:00+06:00"
        record["evidence"] = []
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

    def test_ci_uses_node24_native_immutable_actions(self) -> None:
        checkout = "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0"
        setup_python = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0"
        for workflow_name in ("validate.yml", "release.yml"):
            workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
            with self.subTest(workflow=workflow_name):
                self.assertIn(checkout, workflow)
                self.assertIn(setup_python, workflow)
                self.assertIn("cache-dependency-path: requirements.lock", workflow)
        validate_workflow = (ROOT / ".github/workflows" / "validate.yml").read_text(encoding="utf-8")
        self.assertIn(
            "actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6.0.0",
            validate_workflow,
        )

    def test_domain_method_schema_requires_activation_invariants(self) -> None:
        schema = json.loads((ROOT / "schemas/registry.schema.json").read_text())
        incomplete = {
            "schema": "schemas/registry.schema.json",
            "registry": {
                "id": "registry.probe",
                "type": "domain-method",
                "version": 1,
                "status": "active",
            },
            "items": [{"id": "probe", "name": "Probe", "status": "available"}],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(incomplete, schema)

        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text())
        jsonschema.validate(registry, schema, format_checker=jsonschema.FormatChecker())

        for field in ("requires_domain_handoff", "blocked_handoff_execution"):
            bypass = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text())
            bypass["items"][0][field] = False
            with self.subTest(field=field), self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(bypass, schema)

    def test_compact_dashboard_matches_its_schema(self) -> None:
        schema = json.loads((ROOT / "schemas/dashboard.schema.json").read_text())
        dashboard = create_dashboard(
            "Verify contract", progress=50, active_unit="validate", completed_units=1, total_units=2,
            timestamp="2026-10-17T23:30:00+06:00",
            timezone_name="Asia/Dhaka",
            plan_id="plan-verify", plan_status="READY", surface="hermes-agent",
        )
        jsonschema.validate(dashboard, schema)
        invalid = dict(dashboard, surface="Microsoft Windows")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid, schema)

    def test_platform_neutral_ai_host_contract_is_documented(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        installation = (ROOT / "docs/ai-host-installation.md").read_text(encoding="utf-8")
        hermes_skill = (ROOT / ".agents/skills/atlas-os/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("not a desktop operating system", readme)
        self.assertIn("Hermes Agent", installation)
        self.assertIn("any AI host", installation)
        self.assertNotIn("platforms:", hermes_skill)

    def test_library_record_matches_persistence_schema(self) -> None:
        schema = json.loads((ROOT / "schemas/persistence.schema.json").read_text())
        registry = yaml.safe_load((ROOT / "registries/output-profiles.yaml").read_text())
        profile = next(item for item in registry["items"] if item["id"] == "output.decision-brief")
        record = prepare_library_record(
            "decision-001", profile, timestamp="2026-10-17T23:30:00+06:00",
            timezone_name="Asia/Dhaka",
        )
        jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
        invalid_saved = dict(record)
        invalid_saved["delivery_status"] = "SAVED"
        invalid_saved["persistence_evidence"] = {"claim": True}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid_saved, schema, format_checker=jsonschema.FormatChecker())
        dashboard_schema = json.loads((ROOT / "schemas/dashboard.schema.json").read_text())
        dashboard = create_dashboard(
            "Decide", timestamp="2026-10-17T23:30:00+06:00", library=record,
            timezone_name="Asia/Dhaka",
            plan_id="plan-decide", plan_status="READY",
        )
        jsonschema.validate(dashboard, dashboard_schema, format_checker=jsonschema.FormatChecker())

        task_state = {
            "id": "task-001", "namespace": "TASK", "version": "1",
            "timestamp": "2026-10-17T23:30:00+06:00", "timezone": "Asia/Dhaka",
            "provenance": {"source": "user"}, "status": "ACTIVE",
            "dependencies": [], "replaces": None,
        }
        jsonschema.validate(task_state, schema, format_checker=jsonschema.FormatChecker())

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
