from __future__ import annotations

import unittest

from atlas_runtime.bid_workflow import BidWorkspace, RequirementStatus


class BidWorkflowTests(unittest.TestCase):
    def test_requirement_is_extracted_once_and_updates_preserve_identity(self) -> None:
        workspace = BidWorkspace("2026_PX00011_APIS", deadline="2026-11-30T12:00:00+06:00")
        workspace.add_requirement("R-001", "OEM authorization letter", mandatory=True, owner="OEM")
        workspace.update_requirement("R-001", status=RequirementStatus.SATISFIED, evidence_ref="SP://auth-letter")

        requirement = workspace.requirements["R-001"]
        self.assertEqual(1, len(workspace.requirements))
        self.assertEqual(RequirementStatus.SATISFIED, requirement.status)
        self.assertEqual("SP://auth-letter", requirement.evidence_ref)

    def test_addendum_marks_affected_requirement_for_review(self) -> None:
        workspace = BidWorkspace("2026_PX00011_APIS", deadline="2026-11-30T12:00:00+06:00")
        workspace.add_requirement("R-001", "Delivery period: 180 days", mandatory=True, owner="Technical")
        workspace.update_requirement("R-001", status=RequirementStatus.SATISFIED, evidence_ref="SP://technical-offer")

        workspace.apply_addendum("ADD-02", affected_requirement_ids=["R-001"])

        self.assertEqual(RequirementStatus.REVIEW_REQUIRED, workspace.requirements["R-001"].status)
        self.assertEqual(("ADD-02",), workspace.requirements["R-001"].addenda)

    def test_submission_gate_blocks_missing_mandatory_requirements(self) -> None:
        workspace = BidWorkspace("2026_PX00011_APIS", deadline="2026-11-30T12:00:00+06:00")
        workspace.add_requirement("R-001", "Bid security", mandatory=True, owner="Finance")

        gate = workspace.submission_gate(approved=True)

        self.assertFalse(gate.ready)
        self.assertIn("R-001", gate.blockers)

    def test_submission_gate_requires_explicit_approval_and_receipt_after_submit(self) -> None:
        workspace = BidWorkspace("2026_PX00011_APIS", deadline="2026-11-30T12:00:00+06:00")
        workspace.add_requirement("R-001", "Bid security", mandatory=True, owner="Finance")
        workspace.update_requirement("R-001", status=RequirementStatus.SATISFIED, evidence_ref="SP://security")

        self.assertFalse(workspace.submission_gate(approved=False).ready)
        self.assertTrue(workspace.submission_gate(approved=True).ready)

        workspace.record_submission("eGP", receipt_ref="SP://submission-receipt")
        self.assertEqual("SP://submission-receipt", workspace.submission_receipt_ref)
        self.assertEqual("eGP", workspace.submission_channel)


if __name__ == "__main__":
    unittest.main()
