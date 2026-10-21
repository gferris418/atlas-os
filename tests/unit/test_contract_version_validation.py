from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.validate.validate_repository import (
    ValidationReport,
    _validate_contract_versions,
)


class ContractVersionValidationTests(unittest.TestCase):
    def _fixture(self, root: Path, *, handoff_version: str = "1.2.0") -> dict:
        runtime = root / "atlas_runtime"
        runtime.mkdir()
        (runtime / "handoff.py").write_text(
            f'CONTRACT_VERSION = "{handoff_version}"\n', encoding="utf-8"
        )
        (runtime / "lease.py").write_text(
            'LEASE_CONTRACT_VERSION = "1.0.0"\n', encoding="utf-8"
        )
        (runtime / "authentication.py").write_text(
            'SIGNING_KEY_REGISTRY_VERSION = "1.0.0"\n', encoding="utf-8"
        )
        return {
            "schemas/domain-context-handoff.schema.json": {
                "properties": {"contract_version": {"const": "1.2.0"}}
            },
            "schemas/domain-handoff-receipt.schema.json": {
                "properties": {"contract_version": {"const": "1.2.0"}}
            },
            "schemas/execution-lease.schema.json": {
                "properties": {"contract_version": {"const": "1.0.0"}}
            },
            "schemas/signing-key-registry.schema.json": {
                "properties": {"registry_version": {"const": "1.0.0"}}
            },
        }

    def test_matching_runtime_and_schema_contract_versions_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = ValidationReport()

            _validate_contract_versions(root, self._fixture(root), report)

            self.assertEqual([], report.errors)

    def test_runtime_schema_contract_version_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = ValidationReport()

            _validate_contract_versions(
                root, self._fixture(root, handoff_version="1.2.1"), report
            )

            self.assertEqual(2, len(report.errors))
            self.assertTrue(
                all("runtime/schema contract version mismatch" in error for error in report.errors)
            )
            self.assertTrue(
                all("1.2.1 != 1.2.0" in error for error in report.errors)
            )


if __name__ == "__main__":
    unittest.main()
