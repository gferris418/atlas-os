from __future__ import annotations

import unittest
from pathlib import Path

import yaml

import atlas_runtime
from atlas_runtime import ExecutionEnvelope, execute

ROOT = Path(__file__).resolve().parents[2]


class RequestTriageTests(unittest.TestCase):
    def _triage(self, text: str) -> dict:
        triage = getattr(atlas_runtime, "triage_request", None)
        self.assertTrue(callable(triage))
        return triage(text)

    def test_policy_analysis_stays_direct(self) -> None:
        result = self._triage("Bangladesh Bank foreign exchange policy")
        self.assertEqual("ATLAS_DIRECT", result["collection_mode"])
        self.assertFalse(result["collection_required"])
        self.assertIsNone(result["specialist"])

    def test_bare_strategic_company_target_uses_argus_collection(self) -> None:
        result = self._triage("ST Engineering")
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertEqual("ARGUS", result["specialist"])
        self.assertEqual(["intelligence_collection"], result["capability_requirements"])
        self.assertIn("TARGET_PROFILE", result["collection_types"])

    def test_buyer_product_targets_use_argus_collection(self) -> None:
        for text in (
            "coastal patrol vessel for Bangladesh Coast Guard",
            "seed cum cleaner for BADC",
        ):
            with self.subTest(text=text):
                result = self._triage(text)
                self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
                self.assertIn("BUYER_REQUIREMENT", result["collection_types"])
                self.assertEqual("C3_OPPORTUNITY", result["collection_depth"])

    def test_procurement_plan_uses_argus_collection(self) -> None:
        result = self._triage("share the annual procurement plan of Bangladesh Navy")
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("PROCUREMENT_PLAN", result["collection_types"])

    def test_hybrid_collects_but_keeps_analysis_in_atlas(self) -> None:
        result = self._triage("compare ST Engineering and L3Harris for Bangladesh opportunities")
        self.assertEqual("HYBRID", result["collection_mode"])
        self.assertEqual("ARGUS", result["specialist"])
        self.assertIn("OPPORTUNITY_DISCOVERY", result["collection_types"])

    def test_plain_live_tender_lookup_stays_direct(self) -> None:
        result = self._triage("Find the current Bangladesh Navy tenders.")
        self.assertEqual("ATLAS_DIRECT", result["collection_mode"])
        self.assertNotEqual("INTELLIGENCE", result["route"])

    def test_explanatory_government_question_stays_direct(self) -> None:
        result = self._triage("What is Bangladesh Parjatan Corporation?")
        self.assertEqual("ATLAS_DIRECT", result["collection_mode"])
        self.assertIsNone(result["specialist"])

    def test_writing_has_no_collection(self) -> None:
        result = self._triage("Rewrite this supplier letter in a formal tone.")
        self.assertEqual("NONE", result["collection_mode"])
        self.assertEqual("GENERAL_TASK", result["route"])

    def test_argus_registry_exposes_collection_capability(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text(encoding="utf-8"))
        method = next(item for item in registry["items"] if item["id"] == "domain-method.argus-intelligence")
        self.assertIn("intelligence_collection", method["capabilities"])
        self.assertEqual("2.2.0-rc.1", method["version"])
        self.assertEqual("INTELLIGENCE", method["request_route"])

    def test_execution_result_exposes_collection_mode_in_dashboard(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Rewrite this supplier letter in a formal tone.",
            plan_id="plan-fast-path",
            work_units=[{"id": "rewrite", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertEqual("NONE", result.request_triage["collection_mode"])
        self.assertEqual("NONE", result.dashboard["request_triage"]["collection_mode"])
        self.assertEqual("REQUEST_TRIAGE", result.execution_trace[0])


if __name__ == "__main__":
    unittest.main()
