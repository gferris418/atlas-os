from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

import jsonschema

from atlas_runtime import (
    ExecutionContext,
    prepare_domain_context_handoff,
    verify_domain_context_handoff,
    verify_domain_handoff_receipt,
)

ROOT = Path(__file__).resolve().parents[2]


class DomainContextHandoffTests(unittest.TestCase):
    def _context(self) -> ExecutionContext:
        return ExecutionContext(
            task_id="TASK-SAMPLE-001",
            plan_id="plan-domain-handoff",
            work_unit_id="unit-domain-analysis",
            task_class="ANALYSIS",
        )

    def _task(self) -> dict:
        task = json.loads((ROOT / "tests/fixtures/sample-task.json").read_text())
        task["execution_depth"] = "L2"
        task["domain_alignment"] = {
            "domains": ["planning"],
            "status": "ALIGNED",
            "frameworks": ["framework.iso-example"],
            "applicability": {"framework.iso-example": "APPLICABLE_PENDING_TAILORING"},
            "deviations": [],
            "compliance": "NOT_CLAIMED",
            "evidence": [],
        }
        return task

    def test_prepare_handoff_copies_authoritative_domain_context_exactly(self) -> None:
        task = self._task()
        handoff = prepare_domain_context_handoff(
            task,
            execution_context=self._context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-001",
            created_at="2026-10-18T03:00:00+06:00",
        )
        self.assertEqual("1.1.0", handoff["contract_version"])
        self.assertEqual("ATLAS_OS", handoff["producer"])
        self.assertEqual("ARGUS", handoff["consumer"])
        self.assertEqual(task["id"], handoff["source_task_id"])
        self.assertEqual("plan-domain-handoff", handoff["source_plan_id"])
        self.assertEqual("unit-domain-analysis", handoff["source_work_unit_id"])
        self.assertEqual(task["domain_classification"], handoff["domain_classification"])
        self.assertEqual(task["domain_alignment"], handoff["domain_alignment"])
        self.assertEqual(task["domain_classification"]["unresolved_facets"], handoff["unresolved_material"])
        self.assertEqual(task["domain_classification"]["risk_flags"], handoff["risk_flags"])
        self.assertEqual("PARTIAL", handoff["state"])
        self.assertRegex(handoff["payload_sha256"], r"^sha256:[0-9a-f]{64}$")
        self.assertTrue(verify_domain_context_handoff(handoff))

    def test_handoff_schema_and_receipt_schema_validate(self) -> None:
        task = self._task()
        handoff = prepare_domain_context_handoff(
            task,
            execution_context=self._context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-002",
            created_at="2026-10-18T03:00:00+06:00",
        )
        handoff_schema = json.loads((ROOT / "schemas/domain-context-handoff.schema.json").read_text())
        receipt_schema = json.loads((ROOT / "schemas/domain-handoff-receipt.schema.json").read_text())
        jsonschema.validate(handoff, handoff_schema, format_checker=jsonschema.FormatChecker())
        receipt = {
            "contract_version": handoff["contract_version"],
            "handoff_id": handoff["handoff_id"],
            "payload_sha256": handoff["payload_sha256"],
            "consumer": "ARGUS",
            "status": "ACCEPTED",
            "received_at": "2026-10-18T03:00:01+06:00",
        }
        jsonschema.validate(receipt, receipt_schema, format_checker=jsonschema.FormatChecker())
        self.assertTrue(verify_domain_handoff_receipt(handoff, receipt))

    def test_tampered_handoff_is_rejected(self) -> None:
        handoff = prepare_domain_context_handoff(
            self._task(),
            execution_context=self._context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-003",
            created_at="2026-10-18T03:00:00+06:00",
        )
        tampered = deepcopy(handoff)
        tampered["domain_classification"]["status"] = "CLASSIFIED"
        with self.assertRaisesRegex(ValueError, "integrity"):
            verify_domain_context_handoff(tampered)

    def test_mismatched_return_receipt_is_rejected(self) -> None:
        handoff = prepare_domain_context_handoff(
            self._task(),
            execution_context=self._context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-004",
            created_at="2026-10-18T03:00:00+06:00",
        )
        receipt = {
            "contract_version": "1.1.0",
            "handoff_id": "HANDOFF-OTHER-004",
            "payload_sha256": handoff["payload_sha256"],
            "consumer": "ARGUS",
            "status": "ACCEPTED",
            "received_at": "2026-10-18T03:00:01+06:00",
        }
        with self.assertRaisesRegex(ValueError, "handoff_id"):
            verify_domain_handoff_receipt(handoff, receipt)

    def test_missing_domain_context_cannot_be_handed_to_specialist(self) -> None:
        task = self._task()
        task.pop("domain_alignment")
        with self.assertRaisesRegex(ValueError, "domain_alignment"):
            prepare_domain_context_handoff(
                task,
                execution_context=self._context(),
                consumer="ARGUS",
                handoff_id="HANDOFF-ARGUS-005",
                created_at="2026-10-18T03:00:00+06:00",
            )


if __name__ == "__main__":
    unittest.main()
