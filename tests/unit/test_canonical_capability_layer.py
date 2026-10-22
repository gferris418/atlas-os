from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from atlas_runtime import ExecutionEnvelope, execute, plan_canonical_capabilities

ROOT = Path(__file__).resolve().parents[2]


class CanonicalCapabilityLayerTests(unittest.TestCase):
    def test_registry_defines_exactly_ten_canonical_capabilities(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/canonical-capabilities.yaml").read_text(encoding="utf-8"))
        ids = [item["id"] for item in registry["items"]]
        self.assertEqual(
            [
                "atlas.deep-research",
                "atlas.evidence-governance",
                "argus.collection",
                "atlas.procurement-intelligence",
                "atlas.execution-governance",
                "atlas.agent-security",
                "atlas.commercial-contract-review",
                "atlas.corporate-finance",
                "atlas.economic-policy-intelligence",
                "atlas.classification-crosswalk",
            ],
            ids,
        )
        by_id = {item["id"]: item for item in registry["items"]}
        for capability_id in (
            "atlas.evidence-governance",
            "atlas.execution-governance",
            "atlas.agent-security",
            "atlas.classification-crosswalk",
        ):
            self.assertEqual("KERNEL", by_id[capability_id]["class"])
        self.assertEqual("SPECIALIST", by_id["argus.collection"]["class"])
        self.assertEqual("HYBRID", by_id["atlas.procurement-intelligence"]["class"])

    def test_capability_contract_schemas_are_machine_readable(self) -> None:
        manifest_schema = json.loads((ROOT / "schemas/canonical-capability-registry.schema.json").read_text(encoding="utf-8"))
        request_schema = json.loads((ROOT / "schemas/capability-request.schema.json").read_text(encoding="utf-8"))
        result_schema = json.loads((ROOT / "schemas/capability-result.schema.json").read_text(encoding="utf-8"))
        evidence_schema = json.loads((ROOT / "schemas/evidence-governance.schema.json").read_text(encoding="utf-8"))
        crosswalk_schema = json.loads((ROOT / "schemas/classification-crosswalk.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(["KERNEL", "ROUTED", "SPECIALIST", "HYBRID"], manifest_schema["$defs"]["capability"]["properties"]["class"]["enum"])
        self.assertEqual(["NONE", "ATLAS_DIRECT", "ARGUS_COLLECTION", "HYBRID"], request_schema["properties"]["collection_mode"]["enum"])
        self.assertIn("verification_status", result_schema["required"])
        self.assertEqual(["CONFIRMED", "PROBABLE", "POSSIBLE", "DISPUTED", "UNVERIFIED", "STALE"], evidence_schema["properties"]["status"]["enum"])
        self.assertEqual(["EXACT", "CLOSE", "BROADER", "NARROWER", "RELATED"], crosswalk_schema["properties"]["relationship"]["enum"])

    def test_kernel_services_are_always_active(self) -> None:
        plan = plan_canonical_capabilities(
            "Explain photosynthesis",
            task_classes=("ANSWER",),
            collection_mode="ATLAS_DIRECT",
            collection_types=(),
        )
        self.assertEqual(
            [
                "atlas.evidence-governance",
                "atlas.execution-governance",
                "atlas.agent-security",
                "atlas.classification-crosswalk",
            ],
            plan["kernel"],
        )
        self.assertEqual([], plan["routed"])
        self.assertEqual([], plan["specialist"])

    def test_economic_policy_stays_atlas_direct(self) -> None:
        plan = plan_canonical_capabilities(
            "Bangladesh Bank foreign exchange policy",
            task_classes=("RESEARCH", "ANALYSIS"),
            collection_mode="ATLAS_DIRECT",
            collection_types=(),
        )
        self.assertIn("atlas.economic-policy-intelligence", plan["routed"])
        self.assertNotIn("argus.collection", plan["specialist"])

    def test_argus_collection_depends_only_on_collection_gate(self) -> None:
        direct = plan_canonical_capabilities(
            "ST Engineering",
            task_classes=("ANSWER",),
            collection_mode="ATLAS_DIRECT",
            collection_types=(),
        )
        collected = plan_canonical_capabilities(
            "ST Engineering",
            task_classes=("ANSWER",),
            collection_mode="ARGUS_COLLECTION",
            collection_types=("TARGET_PROFILE", "ENTITY_DOSSIER"),
        )
        self.assertNotIn("argus.collection", direct["specialist"])
        self.assertEqual(["argus.collection"], collected["specialist"])

    def test_procurement_intelligence_is_hybrid_capability(self) -> None:
        plan = plan_canonical_capabilities(
            "Share the annual procurement plan of Bangladesh Navy",
            task_classes=("PLANNING",),
            collection_mode="ARGUS_COLLECTION",
            collection_types=("PROCUREMENT_PLAN", "PROCUREMENT_DISCOVERY"),
        )
        self.assertIn("atlas.procurement-intelligence", plan["routed"])
        self.assertIn("argus.collection", plan["specialist"])

    def test_contract_and_finance_tasks_do_not_imply_argus(self) -> None:
        contract = plan_canonical_capabilities(
            "Review the attached commercial agreement and propose redlines",
            task_classes=("ANALYSIS", "DOCUMENT"),
            collection_mode="NONE",
            collection_types=(),
        )
        finance = plan_canonical_capabilities(
            "Calculate commission margin and FX exposure from the supplied figures",
            task_classes=("ANALYSIS", "DATA"),
            collection_mode="NONE",
            collection_types=(),
        )
        self.assertIn("atlas.commercial-contract-review", contract["routed"])
        self.assertNotIn("argus.collection", contract["specialist"])
        self.assertIn("atlas.corporate-finance", finance["routed"])
        self.assertNotIn("argus.collection", finance["specialist"])

    def test_contract_review_survives_fallback_task_classification(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Review the attached commercial agreement and propose redlines",
            plan_id="plan-contract-review",
            task_id="TASK-CONTRACT-REVIEW",
            work_units=[{"id": "review", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertIn("atlas.commercial-contract-review", result.capability_plan["routed"])
        self.assertNotIn("argus.collection", result.capability_plan["specialist"])

    def test_clause_analysis_routes_to_contract_review(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Analyze the indemnity clause in the attached agreement",
            plan_id="plan-clause-analysis",
            task_id="TASK-CLAUSE-ANALYSIS",
            work_units=[{"id": "analyze", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertIn("atlas.commercial-contract-review", result.capability_plan["routed"])
        self.assertNotIn("argus.collection", result.capability_plan["specialist"])

    def test_public_equity_research_excludes_corporate_finance(self) -> None:
        plan = plan_canonical_capabilities(
            "Research public-equity investments by comparing the cash flow of Apple and Microsoft",
            task_classes=("RESEARCH", "ANALYSIS"),
            collection_mode="ATLAS_DIRECT",
            collection_types=(),
        )
        self.assertNotIn("atlas.corporate-finance", plan["routed"])

    def test_generic_policy_monitoring_does_not_imply_procurement(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Monitor Bangladesh Bank monetary policy circulars",
            plan_id="plan-policy-monitor",
            task_id="TASK-POLICY-MONITOR",
            work_units=[{"id": "monitor", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertIn("atlas.economic-policy-intelligence", result.capability_plan["routed"])
        self.assertNotIn("atlas.procurement-intelligence", result.capability_plan["routed"])
        self.assertIn("argus.collection", result.capability_plan["specialist"])

    def test_explicit_deep_research_can_be_hybrid(self) -> None:
        plan = plan_canonical_capabilities(
            "Deep research ST Engineering maritime procurement opportunities in Bangladesh",
            task_classes=("RESEARCH", "ANALYSIS"),
            collection_mode="HYBRID",
            collection_types=("ENTITY_DOSSIER", "OPPORTUNITY_DISCOVERY"),
        )
        self.assertIn("atlas.deep-research", plan["routed"])
        self.assertIn("atlas.procurement-intelligence", plan["routed"])
        self.assertIn("argus.collection", plan["specialist"])

    def test_live_execution_projects_the_canonical_capability_plan(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Bangladesh Bank foreign exchange policy",
            plan_id="plan-economic-policy",
            task_id="TASK-ECONOMIC-POLICY",
            work_units=[{"id": "analyze", "status": "PENDING", "dependencies": []}],
            clarification_status="RESOLVED",
        ))
        self.assertIn("atlas.economic-policy-intelligence", result.capability_plan["routed"])
        self.assertNotIn("argus.collection", result.capability_plan["specialist"])
        self.assertEqual(result.capability_plan, result.dashboard["capability_plan"])
        self.assertIn("CAPABILITY_PLANNING", result.execution_trace)


if __name__ == "__main__":
    unittest.main()
