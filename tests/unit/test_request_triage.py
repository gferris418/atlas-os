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
        self.assertTrue(callable(triage), "atlas_runtime.triage_request must be public")
        return triage(text)

    def test_general_search_stays_on_direct_atlas_path(self) -> None:
        result = self._triage("Find the current Bangladesh Railway tenders.")
        self.assertEqual("GENERAL_SEARCH", result["route"])
        self.assertIsNone(result["specialist"])
        self.assertEqual([], result["capability_requirements"])

    def test_general_task_stays_on_direct_atlas_path(self) -> None:
        result = self._triage("Rewrite this supplier letter in a formal tone.")
        self.assertEqual("GENERAL_TASK", result["route"])
        self.assertIsNone(result["specialist"])

    def test_intelligence_objective_routes_to_argus(self) -> None:
        result = self._triage(
            "Find Bangladesh Railway opportunities we should pursue, rank them by win probability, "
            "identify competitors and decision makers, and monitor material developments."
        )
        self.assertEqual("INTELLIGENCE", result["route"])
        self.assertEqual("ARGUS", result["specialist"])
        self.assertEqual(["intelligence_analysis"], result["capability_requirements"])
        self.assertIn("OPPORTUNITY_INTELLIGENCE", result["intelligence_types"])
        self.assertIn("COMPETITIVE_INTELLIGENCE", result["intelligence_types"])
        self.assertIn("MONITORING_INTELLIGENCE", result["intelligence_types"])

    def test_assessing_opportunities_is_intelligence_but_plain_tender_lookup_is_not(self) -> None:
        assessment = self._triage(
            "Find and assess public procurement opportunities for coastal surveillance radar "
            "for Bangladesh Navy using public sources only."
        )
        lookup = self._triage("Find the current Bangladesh Navy tenders.")
        self.assertEqual("INTELLIGENCE", assessment["route"])
        self.assertIn("OPPORTUNITY_INTELLIGENCE", assessment["intelligence_types"])
        self.assertEqual("GENERAL_SEARCH", lookup["route"])

    def test_government_mention_alone_does_not_activate_argus(self) -> None:
        result = self._triage("What is Bangladesh Parjatan Corporation?")
        self.assertEqual("GENERAL_SEARCH", result["route"])
        self.assertIsNone(result["specialist"])

    def test_argus_registry_exposes_one_generic_intelligence_capability(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text(encoding="utf-8"))
        method = next(item for item in registry["items"] if item["id"] == "domain-method.argus-intelligence")
        self.assertIn("intelligence_analysis", method["capabilities"])
        self.assertEqual("INTELLIGENCE", method["request_route"])

    def test_execution_result_exposes_triage_before_deep_domain_work(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Rewrite this supplier letter in a formal tone.",
            plan_id="plan-fast-path",
            work_units=[{"id": "rewrite", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertEqual("GENERAL_TASK", getattr(result, "request_route", None))
        self.assertEqual("REQUEST_TRIAGE", result.execution_trace[0])
        self.assertNotIn("DOMAIN_CLASSIFICATION", result.execution_trace)
        self.assertNotIn("DOMAIN_FRAMEWORK_ALIGNMENT", result.execution_trace)

    def test_direct_route_cannot_be_silently_escalated_to_argus_downstream(self) -> None:
        result = execute(ExecutionEnvelope(
            objective=(
                "Research and write a report on public procurement opportunities "
                "for Bangladesh Navy coastal surveillance radar"
            ),
            task_id="TASK-DIRECT-OPPORTUNITY-REPORT",
            plan_id="plan-direct-opportunity-report",
            work_units=[{"id": "research", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
            timestamp="2026-10-22T01:20:00+06:00",
            timezone_name="Asia/Dhaka",
        ))
        self.assertNotEqual("INTELLIGENCE", result.request_route)
        self.assertNotIn(
            "domain-method.argus-intelligence",
            {provider["id"] for provider in result.routing_preview["providers"]},
        )
        self.assertNotIn("intelligence_analysis", result.routing_preview["requirements"])
        self.assertNotIn(
            "government_public_sector_opportunity_intelligence",
            result.routing_preview["requirements"],
        )


if __name__ == "__main__":
    unittest.main()
