from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_manifest_is_only_product_version_authority(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertEqual("2.0.0-rc.2", manifest["product"]["version"])
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

    def test_structured_tasks_require_domain_alignment(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        jsonschema.validate(task, schema)
        task.pop("domain_alignment")
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(task, schema)

    def test_l0_task_may_omit_explicit_domain_alignment(self) -> None:
        schema = json.loads((ROOT / "schemas/task.schema.json").read_text())
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        task["execution_depth"] = "L0"
        task.pop("domain_alignment")
        jsonschema.validate(task, schema)


if __name__ == "__main__":
    unittest.main()

