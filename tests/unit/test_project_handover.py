from __future__ import annotations

import unittest

from atlas_runtime.project_handover import AwardHandover, HandoverItemStatus


class AwardHandoverTests(unittest.TestCase):
    def test_preserves_px_identity_and_builds_ops_project_identity(self) -> None:
        handover = AwardHandover("2026_PX00011_APIS", award_ref="AWD-001", contract_ref="CTR-001")

        self.assertEqual("2026_PX00011_APIS", handover.px_id)
        self.assertEqual("2026_PX00011_APIS", handover.project_id)
        self.assertEqual("OPS/Projects/2026_PX00011_APIS", handover.project_workspace)

    def test_required_handover_items_need_evidence_and_owner(self) -> None:
        handover = AwardHandover("2026_PX00011_APIS", award_ref="AWD-001", contract_ref="CTR-001")
        handover.add_item("H-001", "Final accepted technical scope", owner="Project", required=True)

        gate = handover.readiness_gate(approved=True)
        self.assertFalse(gate.ready)
        self.assertIn("H-001", gate.blockers)

        handover.complete_item("H-001", evidence_ref="SP://final-scope")
        self.assertEqual(HandoverItemStatus.COMPLETE, handover.items["H-001"].status)
        self.assertEqual("Project", handover.items["H-001"].owner)

    def test_contract_variance_blocks_readiness_until_resolved(self) -> None:
        handover = AwardHandover("2026_PX00011_APIS", award_ref="AWD-001", contract_ref="CTR-001")
        handover.add_item("H-001", "Payment schedule", owner="Finance", required=True)
        handover.complete_item("H-001", evidence_ref="SP://payment-schedule")
        handover.add_variance("V-001", "Contract payment terms differ from final bid")

        self.assertFalse(handover.readiness_gate(approved=True).ready)
        handover.resolve_variance("V-001", resolution_ref="SP://approved-variance")
        self.assertTrue(handover.readiness_gate(approved=True).ready)

    def test_readiness_requires_atlas_approval(self) -> None:
        handover = AwardHandover("2026_PX00011_APIS", award_ref="AWD-001", contract_ref="CTR-001")
        handover.add_item("H-001", "Milestone register", owner="Project", required=True)
        handover.complete_item("H-001", evidence_ref="SP://milestones")

        gate = handover.readiness_gate(approved=False)
        self.assertFalse(gate.ready)
        self.assertIn("ATLAS_APPROVAL", gate.blockers)

    def test_activation_records_acceptance_without_changing_lineage(self) -> None:
        handover = AwardHandover("2026_PX00011_APIS", award_ref="AWD-001", contract_ref="CTR-001")
        handover.add_item("H-001", "Risk register", owner="Project", required=True)
        handover.complete_item("H-001", evidence_ref="SP://risks")

        handover.activate_project(approved=True, acceptance_ref="SP://handover-acceptance")

        self.assertTrue(handover.activated)
        self.assertEqual("SP://handover-acceptance", handover.acceptance_ref)
        self.assertEqual("2026_PX00011_APIS", handover.project_id)


if __name__ == "__main__":
    unittest.main()
