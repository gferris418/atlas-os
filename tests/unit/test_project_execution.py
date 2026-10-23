from __future__ import annotations

import unittest

from atlas_runtime.project_execution import MilestoneStatus, ProjectExecution


class ProjectExecutionTests(unittest.TestCase):
    def test_milestone_preserves_px_and_contract_lineage(self) -> None:
        project = ProjectExecution("2026_PX00011_APIS", contract_ref="CTR-001")
        project.add_milestone(
            "M-001",
            "Factory acceptance test",
            owner="OEM",
            due_date="2026-12-15",
            contract_obligation_ref="CTR-001:SOW:4.2",
            payment_trigger=True,
        )

        milestone = project.milestones["M-001"]
        self.assertEqual("2026_PX00011_APIS", project.px_id)
        self.assertEqual("CTR-001:SOW:4.2", milestone.contract_obligation_ref)
        self.assertTrue(milestone.payment_trigger)

    def test_dependency_blocks_acceptance(self) -> None:
        project = ProjectExecution("2026_PX00011_APIS", contract_ref="CTR-001")
        project.add_milestone("M-001", "Site ready", owner="Local", due_date="2026-12-01", contract_obligation_ref="CTR-001:SOW:2")
        project.add_milestone("M-002", "Commissioning", owner="OEM", due_date="2026-12-20", contract_obligation_ref="CTR-001:SOW:5", dependencies=["M-001"])

        with self.assertRaises(ValueError):
            project.accept_milestone("M-002", evidence_ref="SP://commissioning")

        project.accept_milestone("M-001", evidence_ref="SP://site-ready")
        project.accept_milestone("M-002", evidence_ref="SP://commissioning")
        self.assertEqual(MilestoneStatus.ACCEPTED, project.milestones["M-002"].status)

    def test_open_issue_blocks_milestone_acceptance(self) -> None:
        project = ProjectExecution("2026_PX00011_APIS", contract_ref="CTR-001")
        project.add_milestone("M-001", "Harbour acceptance test", owner="Project", due_date="2026-12-20", contract_obligation_ref="CTR-001:SOW:6")
        project.add_issue("I-001", "Customer test observation unresolved", owner="Technical", milestone_id="M-001")

        with self.assertRaises(ValueError):
            project.accept_milestone("M-001", evidence_ref="SP://hat")

        project.resolve_issue("I-001", resolution_ref="SP://issue-resolution")
        project.accept_milestone("M-001", evidence_ref="SP://hat")
        self.assertEqual(MilestoneStatus.ACCEPTED, project.milestones["M-001"].status)

    def test_payment_ready_requires_accepted_payment_trigger_with_evidence(self) -> None:
        project = ProjectExecution("2026_PX00011_APIS", contract_ref="CTR-001")
        project.add_milestone("M-001", "Delivery acceptance", owner="Project", due_date="2026-12-20", contract_obligation_ref="CTR-001:SOW:7", payment_trigger=True)

        self.assertEqual((), project.payment_ready_milestones())
        project.accept_milestone("M-001", evidence_ref="SP://acceptance-certificate")
        self.assertEqual(("M-001",), project.payment_ready_milestones())

    def test_project_completion_requires_all_required_milestones_accepted(self) -> None:
        project = ProjectExecution("2026_PX00011_APIS", contract_ref="CTR-001")
        project.add_milestone("M-001", "Training", owner="OEM", due_date="2026-12-20", contract_obligation_ref="CTR-001:SOW:8", required=True)

        self.assertFalse(project.completion_gate().ready)
        project.accept_milestone("M-001", evidence_ref="SP://training-acceptance")
        self.assertTrue(project.completion_gate().ready)


if __name__ == "__main__":
    unittest.main()
