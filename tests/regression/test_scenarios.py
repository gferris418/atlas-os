from __future__ import annotations

import unittest

from atlas_runtime import ApprovalRequired, align_domain_practices, determine_execution_depth, require_approval, verify_evidence


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
]


class ScenarioRegressionTests(unittest.TestCase):
    def test_execution_depth_scenarios(self) -> None:
        for identifier, title, inputs, expected in SCENARIOS:
            with self.subTest(identifier=identifier, title=title):
                self.assertEqual(expected, determine_execution_depth(**inputs))

    def test_destructive_scenario_requires_approval(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("delete")

    def test_supplied_approval_is_scoped(self) -> None:
        self.assertTrue(require_approval("publish", {"status": "APPROVED", "scope": ["publish"]}))
        with self.assertRaises(ApprovalRequired):
            require_approval("delete", {"status": "APPROVED", "scope": ["publish"]})

    def test_insufficient_evidence_remains_unverified(self) -> None:
        self.assertEqual("UNKNOWN", verify_evidence({"class": "UNKNOWN"})["class"])

    def test_domain_work_without_framework_enters_research_required(self) -> None:
        result = align_domain_practices("unregistered-domain", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", result["status"])
        self.assertEqual("UNVERIFIED", result["compliance"])


if __name__ == "__main__":
    unittest.main()

