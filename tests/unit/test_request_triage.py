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

    def test_procurement_forecast_uses_hybrid_collection(self) -> None:
        result = self._triage("Forecast likely Bangladesh Navy procurements over 24 months")
        self.assertEqual("HYBRID", result["collection_mode"])
        self.assertIn("PROCUREMENT_DISCOVERY", result["collection_types"])

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

    def test_ordinary_operations_do_not_become_bare_targets(self) -> None:
        for text in ("2 + 2", "Convert 10 USD to EUR", "Debug this SQL query"):
            with self.subTest(text=text):
                result = self._triage(text)
                self.assertEqual("NONE", result["collection_mode"])
                self.assertEqual("GENERAL_TASK", result["route"])

    def test_supplied_procurement_document_transformation_stays_direct(self) -> None:
        result = self._triage("Summarize the attached procurement plan.")
        self.assertEqual("NONE", result["collection_mode"])
        self.assertEqual("GENERAL_TASK", result["route"])

    def test_supplied_document_does_not_suppress_independent_monitoring(self) -> None:
        result = self._triage(
            "Summarize the attached report, then monitor ST Engineering for new procurement opportunities."
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("MONITORING", result["collection_types"])
        self.assertIn("OPPORTUNITY_DISCOVERY", result["collection_types"])
        self.assertEqual("C4_MONITOR", result["collection_depth"])

    def test_argus_registry_exposes_collection_capability(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text(encoding="utf-8"))
        method = next(item for item in registry["items"] if item["id"] == "domain-method.argus-intelligence")
        self.assertIn("intelligence_collection", method["capabilities"])
        self.assertEqual("2.2.0-rc.2", method["version"])
        self.assertEqual("INTELLIGENCE", method["request_route"])
        self.assertIn("PLANNING", method["task_classes"])
        self.assertIn("WORKFLOW", method["task_classes"])

    def test_direct_request_cannot_force_collection_capability(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Explain photosynthesis.",
            plan_id="plan-direct-guard",
            task_id="TASK-DIRECT-GUARD",
            work_units=[{"id": "answer", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            capability_requirements=("intelligence_collection",),
            timestamp="2026-10-22T05:20:00+06:00",
            timezone_name="Asia/Dhaka",
        ))
        self.assertEqual("ATLAS_DIRECT", result.request_triage["collection_mode"])
        self.assertNotIn("intelligence_collection", result.routing_preview["requirements"])
        self.assertFalse(any(
            provider["id"] == "domain-method.argus-intelligence"
            for provider in result.routing_preview["providers"]
        ))

    def test_collection_preview_contains_bound_mission(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="ST Engineering",
            plan_id="plan-collection-mission",
            task_id="TASK-COLLECTION-MISSION",
            work_units=[{"id": "collect", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            timestamp="2026-10-22T05:20:00+06:00",
            timezone_name="Asia/Dhaka",
        ))
        mission = result.routing_preview["collection_mission"]
        self.assertIsNotNone(mission)
        self.assertEqual("TASK-COLLECTION-MISSION", mission["source_task_id"])
        self.assertEqual("plan-collection-mission", mission["source_plan_id"])
        self.assertEqual("ARGUS_COLLECTION", mission["collection_mode"])
        self.assertEqual([], [gate for gate in result.routing_preview["unresolved_gates"] if "collection_mission" in gate])

    def test_historical_procurement_mission_preserves_requested_period(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Find the annual procurement plan of Bangladesh Navy for 2020",
            plan_id="plan-historical-procurement",
            task_id="TASK-HISTORICAL-PROCUREMENT",
            work_units=[{"id": "collect", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            timestamp="2026-10-22T05:20:00+06:00",
            timezone_name="Asia/Dhaka",
        ))
        mission = result.routing_preview["collection_mission"]
        self.assertEqual("2020", mission["time_horizon"])
        self.assertEqual("HISTORICAL", mission["freshness_requirement"])

    def test_sensitive_collection_preserves_risk_classification(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Assess coastal surveillance radar for Bangladesh Navy",
            plan_id="plan-sensitive-collection",
            task_id="TASK-SENSITIVE-COLLECTION",
            work_units=[{"id": "assess", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            timestamp="2026-10-22T05:20:00+06:00",
            timezone_name="Asia/Dhaka",
        ))
        self.assertEqual("HYBRID", result.request_triage["collection_mode"])
        self.assertIn("defense", result.domain_classification["risk_flags"])
        self.assertIn("dual-use", result.domain_classification["risk_flags"])
        self.assertIn("national-security", result.routing_preview["collection_mission"]["risk_flags"])

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
