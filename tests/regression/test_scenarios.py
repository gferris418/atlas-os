from __future__ import annotations

import unittest

from pathlib import Path

import yaml

from atlas_runtime import (
    ApprovalRequired,
    align_domain_practices,
    classify_domain_context,
    determine_execution_depth,
    require_approval,
    select_output_profile,
    verify_evidence,
)


ROOT = Path(__file__).resolve().parents[2]


SCENARIOS = [
    ("REG-001", "simple factual answer", {"steps": 1}, "L0"),
    ("REG-002", "current web research", {"steps": 3, "ambiguity": True}, "L2"),
    ("REG-003", "private connected-source research", {"steps": 4}, "L2"),
    ("REG-004", "document generation", {"steps": 4}, "L2"),
    ("REG-005", "coding task", {"steps": 6}, "L2"),
    ("REG-006", "destructive external action", {"steps": 4, "risk": "high", "external_action": True}, "L4"),
    ("REG-007", "insufficient evidence", {"steps": 3, "ambiguity": True}, "L2"),
    ("REG-008", "conflicting sources", {"steps": 4, "ambiguity": True}, "L2"),
    ("REG-009", "interrupted multi-stage task", {"steps": 8}, "L3"),
    ("REG-010", "resumed task", {"steps": 5}, "L2"),
    ("REG-011", "canonical-state replacement", {"steps": 7, "risk": "high"}, "L3"),
    ("REG-012", "unresolved dependency", {"steps": 6, "ambiguity": True}, "L2"),
    ("REG-013", "release with open blocker", {"steps": 8, "risk": "high"}, "L3"),
    ("REG-014", "cross-surface adapter behavior", {"steps": 7}, "L2"),
    ("REG-015", "user changes objective mid-task", {"steps": 5, "ambiguity": True}, "L2"),
    ("REG-016", "user supplies approval", {"steps": 4, "external_action": True}, "L2"),
    ("REG-017", "domain framework alignment", {"steps": 4}, "L2"),
    ("REG-018", "taxonomy and industry classification", {"steps": 4, "ambiguity": True}, "L2"),
    ("REG-019", "proportional output profile selection", {"steps": 2}, "L1"),
]


class ScenarioRegressionTests(unittest.TestCase):
    def test_execution_depth_scenarios(self) -> None:
        for identifier, title, inputs, expected in SCENARIOS:
            with self.subTest(identifier=identifier, title=title):
                self.assertEqual(expected, determine_execution_depth(**inputs))

    def test_destructive_scenario_requires_approval(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("delete", action_classes=["destructive_action"])

    def test_supplied_approval_is_scoped(self) -> None:
        approval = {
            "status": "APPROVED", "scope": ["publish"], "action_type": "publish",
            "target_id": "release:atlas", "input_sha256": "sha256:" + "a" * 64,
            "precondition_revision": "rev-1", "approver_identity": "user:maintainer",
            "id": "APR-PUBLISH-REGRESSION", "required": True, "reason": "Release approval",
            "requested_at": "2026-10-18T05:00:00Z", "approved_at": "2026-10-18T05:01:00Z",
            "issued_at": "2026-10-18T05:00:00Z", "expires_at": "2099-10-18T06:00:00Z",
            "policy_revision": "approvals-v2",
            "source_task_id": "TASK-ATLAS-RELEASE", "source_plan_id": "plan-release",
            "source_work_unit_id": "unit-publish", "handoff_id": None,
        }
        self.assertTrue(require_approval(
            "publish", approval, action_classes=["publication"], target_id="release:atlas",
            input_sha256="sha256:" + "a" * 64, precondition_revision="rev-1",
            policy_revision="approvals-v2",
            source_task_id="TASK-ATLAS-RELEASE", source_plan_id="plan-release",
            source_work_unit_id="unit-publish", handoff_id=None,
        ))
        with self.assertRaises(ApprovalRequired):
            require_approval(
                "delete", approval, action_classes=["destructive_action"], target_id="release:atlas",
                input_sha256="sha256:" + "a" * 64, precondition_revision="rev-1",
                policy_revision="approvals-v2",
                source_task_id="TASK-ATLAS-RELEASE", source_plan_id="plan-release",
                source_work_unit_id="unit-publish", handoff_id=None,
            )

    def test_insufficient_evidence_remains_unverified(self) -> None:
        self.assertEqual("UNKNOWN", verify_evidence({"class": "UNKNOWN"})["class"])

    def test_domain_work_without_framework_enters_research_required(self) -> None:
        result = align_domain_practices("unregistered-domain", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", result["status"])
        self.assertEqual("UNVERIFIED", result["compliance"])

    def test_defence_radar_prompt_is_classified_before_framework_selection(self) -> None:
        registry = yaml.safe_load(
            (ROOT / "registries/classifications.yaml").read_text(encoding="utf-8")
        )
        result = classify_domain_context(
            "coastal surveillance radar for Bangladesh navy",
            registry["items"],
            required_facets=("jurisdiction", "operator-industry", "capability", "lifecycle-stage"),
        )
        self.assertEqual("PARTIAL", result["status"])
        self.assertEqual(["lifecycle-stage"], result["unresolved_facets"])
        self.assertEqual("BD", result["facets"]["jurisdiction"][0]["code"])
        self.assertEqual("8422", result["facets"]["operator-industry"][0]["code"])
        self.assertIn("defense", result["risk_flags"])
        self.assertIn("operational-security", result["risk_flags"])

    def test_research_uses_sourced_output_without_overriding_explicit_choice(self) -> None:
        registry = yaml.safe_load(
            (ROOT / "registries/output-profiles.yaml").read_text(encoding="utf-8")
        )
        selected = select_output_profile(["RESEARCH", "ANALYSIS"], registry["items"])
        self.assertEqual("output.research-sourced", selected["id"])
        requested = select_output_profile(
            ["RESEARCH"], registry["items"], requested_id="output.answer-concise"
        )
        self.assertEqual("output.answer-concise", requested["id"])


if __name__ == "__main__":
    unittest.main()

