from __future__ import annotations

import unittest

from atlas_runtime import ExecutionEnvelope, execute


class ArgusAuthorizationTests(unittest.TestCase):
    def _envelope(self, **overrides):
        values = {
            "objective": "ST Engineering",
            "plan_id": "plan-explicit-argus-approval",
            "task_id": "TASK-EXPLICIT-ARGUS-APPROVAL",
            "work_units": [{"id": "collect", "status": "PENDING", "dependencies": []}],
            "clarification_status": "RESOLVED",
            "timestamp": "2026-10-22T20:00:00+06:00",
            "timezone_name": "Asia/Dhaka",
        }
        values.update(overrides)
        return ExecutionEnvelope(**values)

    def test_argus_requires_explicit_authorization_after_routing_preview_approval(self) -> None:
        initial = execute(self._envelope())
        digest = initial.routing_preview["digest"]

        result = execute(self._envelope(
            routing_approval_status="APPROVED",
            routing_preview_digest=digest,
            argus_approval_status="PENDING",
        ))

        contract = result.routing_preview["activation_contract"]
        self.assertEqual("2.0", contract["version"])
        self.assertEqual("ARGUS_COLLECTION", contract["route"]["collection_mode"])
        self.assertTrue(contract["argus"]["required"])
        self.assertEqual("PENDING", contract["argus"]["authorization"]["status"])
        self.assertEqual("NOT_AUTHORIZED", contract["argus"]["activation"]["status"])
        self.assertIn("ARGUS_EXPLICIT_APPROVAL_REQUIRED", contract["blockers"])
        self.assertEqual("AWAITING_APPROVAL", result.state)
        self.assertEqual("ARGUS_APPROVAL", result.dashboard["active_stage"])
        self.assertEqual([], list(result.routing_decisions))

    def test_explicit_argus_authorization_allows_same_digest_bound_proposal_to_route(self) -> None:
        initial = execute(self._envelope())
        digest = initial.routing_preview["digest"]

        result = execute(self._envelope(
            routing_approval_status="APPROVED",
            routing_preview_digest=digest,
            argus_approval_status="APPROVED",
            argus_approval_digest=digest,
        ))

        contract = result.routing_preview["activation_contract"]
        self.assertEqual(digest, result.routing_preview["digest"])
        self.assertEqual("APPROVED", contract["argus"]["authorization"]["status"])
        self.assertEqual(digest, contract["argus"]["authorization"]["bound_preview_digest"])
        self.assertEqual("AUTHORIZED", contract["argus"]["activation"]["status"])
        self.assertNotIn("ARGUS_EXPLICIT_APPROVAL_REQUIRED", contract["blockers"])
        self.assertTrue(any(
            decision["provider_id"] == "domain-method.argus-intelligence"
            and decision["status"] == "ROUTED"
            for decision in result.routing_decisions
        ))

    def test_stale_argus_authorization_digest_fails_closed(self) -> None:
        initial = execute(self._envelope())
        digest = initial.routing_preview["digest"]

        result = execute(self._envelope(
            routing_approval_status="APPROVED",
            routing_preview_digest=digest,
            argus_approval_status="APPROVED",
            argus_approval_digest="sha256:stale",
        ))

        contract = result.routing_preview["activation_contract"]
        self.assertEqual("STALE", contract["argus"]["authorization"]["status"])
        self.assertEqual("sha256:stale", contract["argus"]["authorization"]["bound_preview_digest"])
        self.assertEqual("NOT_AUTHORIZED", contract["argus"]["activation"]["status"])
        self.assertIn("ARGUS_APPROVAL_DIGEST_MISMATCH", contract["blockers"])
        self.assertEqual("AWAITING_APPROVAL", result.state)
        self.assertEqual([], list(result.routing_decisions))

    def test_non_argus_work_does_not_require_argus_authorization(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Rewrite this supplier letter in a formal tone.",
            plan_id="plan-no-argus-approval",
            task_id="TASK-NO-ARGUS-APPROVAL",
            work_units=[{"id": "rewrite", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            argus_approval_status="PENDING",
        ))

        contract = result.routing_preview["activation_contract"]
        self.assertFalse(contract["argus"]["required"])
        self.assertEqual("NOT_REQUIRED", contract["argus"]["authorization"]["status"])
        self.assertEqual("NOT_REQUIRED", contract["argus"]["activation"]["status"])
        self.assertNotIn("ARGUS_EXPLICIT_APPROVAL_REQUIRED", contract["blockers"])

    def test_rejected_argus_authorization_is_fail_closed(self) -> None:
        initial = execute(self._envelope())
        digest = initial.routing_preview["digest"]

        result = execute(self._envelope(
            routing_approval_status="APPROVED",
            routing_preview_digest=digest,
            argus_approval_status="REJECTED",
            argus_approval_digest=digest,
        ))

        contract = result.routing_preview["activation_contract"]
        self.assertEqual("REJECTED", contract["argus"]["authorization"]["status"])
        self.assertEqual(digest, contract["argus"]["authorization"]["bound_preview_digest"])
        self.assertEqual("NOT_AUTHORIZED", contract["argus"]["activation"]["status"])
        self.assertEqual("BLOCKED", result.state)
        self.assertEqual([], list(result.routing_decisions))


if __name__ == "__main__":
    unittest.main()
