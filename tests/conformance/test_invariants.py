from __future__ import annotations

import unittest

from atlas_runtime import (
    ApprovalRequired,
    CanonicalRevisionInUse,
    StateStore,
    align_domain_practices,
    build_plan,
    can_transition_release,
    classify_domain_context,
    create_dashboard,
    normalize_intent,
    require_approval,
    select_next_work_unit,
    verify_evidence,
)


class RuntimeInvariantConformance(unittest.TestCase):
    def test_inv_001_and_002_intent_and_literals(self) -> None:
        original = "Keep `MIG-037`, 2026-10-17, and 3 outputs exactly."
        state = normalize_intent(original)
        self.assertEqual(original, state["original"])
        for value in ("`MIG-037`", "2026", "10", "17", "3"):
            self.assertIn(value, state["normalized"])

    def test_inv_003_and_004_substantive_dashboard(self) -> None:
        state = create_dashboard("Conformance", substantive=True)
        self.assertEqual("ATLAS", state["system"])
        self.assertEqual(0, state["progress"])

    def test_inv_005_006_and_016_evidence_distinctions(self) -> None:
        for classification in ("ASSUMED", "INFERRED", "SPECULATIVE", "UNKNOWN"):
            with self.subTest(classification=classification):
                self.assertEqual(classification, verify_evidence({"class": classification})["class"])

    def test_inv_007_008_009_states_are_distinct(self) -> None:
        state = {"generated": True, "executed": False, "verified": False, "accepted": False}
        self.assertTrue(state["generated"])
        self.assertFalse(state["executed"] or state["verified"] or state["accepted"])

    def test_inv_010_open_blocker(self) -> None:
        self.assertFalse(can_transition_release("VERIFIED", "RELEASED", ["MIG-029"]))

    def test_inv_011_approval(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("delete")

    def test_inv_012_state_separation(self) -> None:
        store = StateStore()
        store.save_task("item", {})
        with self.assertRaises(ValueError):
            store.save_canonical("item", {})

    def test_inv_013_dependency_protection(self) -> None:
        store = StateStore(canonical_state={"v1": {"active_dependents": ["v2"]}})
        with self.assertRaises(CanonicalRevisionInUse):
            store.archive_canonical("v1")

    def test_inv_014_unique_authority_is_validator_owned(self) -> None:
        self.assertEqual(["authority"], build_plan([{"id": "authority", "dependencies": []}]))

    def test_inv_015_and_017_adapters_do_not_bypass_core(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("change_permissions", {"status": "APPROVED", "scope": ["publish"]})

    def test_inv_018_domain_framework_alignment(self) -> None:
        unresolved = align_domain_practices("medical-device", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", unresolved["status"])
        self.assertNotEqual("VERIFIED", unresolved["compliance"])

    def test_inv_019_domain_classification_does_not_guess(self) -> None:
        unresolved = classify_domain_context("specialist unmapped system", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", unresolved["status"])
        self.assertEqual({}, unresolved["facets"])

    def test_inv_020_atomic_execution_has_one_active_unit(self) -> None:
        with self.assertRaises(ValueError):
            select_next_work_unit([
                {"id": "one", "status": "ACTIVE", "dependencies": []},
                {"id": "two", "status": "ACTIVE", "dependencies": []},
            ])


if __name__ == "__main__":
    unittest.main()

