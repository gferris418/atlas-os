from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

import atlas_runtime
from atlas_runtime import plan_canonical_capabilities

ROOT = Path(__file__).resolve().parents[2]


class ArgusV3CommercialOpportunityIntegrationTests(unittest.TestCase):
    def _triage(self, text: str) -> dict:
        return atlas_runtime.triage_request(text)

    def test_collection_contract_accepts_argus_v3_types(self) -> None:
        schema = json.loads((ROOT / "schemas/collection-mission.schema.json").read_text(encoding="utf-8"))
        values = set(schema["properties"]["collection_types"]["items"]["enum"])
        self.assertTrue({
            "NEED_GAP", "POLICY_DRIVER", "PROGRAMME_PROJECT", "APPROVAL_STATUS",
            "SUPPLIER_PROFILE", "REFERENCE_PROJECT", "EXPORT_FEASIBILITY", "PARTNERABILITY",
            "OPPORTUNITY_DEVELOPMENT", "OPPORTUNITY_MATCHING", "EXPANSION_DISCOVERY", "RAPID_TENDER",
        } <= values)

    def test_need_gap_discovery_activates_argus_before_procurement(self) -> None:
        result = self._triage(
            "What capability gaps could Bangladesh Coast Guard address with foreign technology?"
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("NEED_GAP", result["collection_types"])
        self.assertIn("OPPORTUNITY_DISCOVERY", result["collection_types"])
        self.assertEqual("C3_OPPORTUNITY", result["collection_depth"])

    def test_supply_first_discovery_maps_technology_to_government_need(self) -> None:
        result = self._triage(
            "Where could ST Engineering coastal surveillance technology fit in Bangladesh government?"
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("PRODUCT_CAPABILITY", result["collection_types"])
        self.assertIn("OPPORTUNITY_MATCHING", result["collection_types"])
        self.assertIn("OPPORTUNITY_DISCOVERY", result["collection_types"])

    def test_opportunity_development_is_not_tender_dependent(self) -> None:
        result = self._triage(
            "Identify government problems where we could introduce an internationally proven solution and shape a future opportunity."
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("NEED_GAP", result["collection_types"])
        self.assertIn("OPPORTUNITY_DEVELOPMENT", result["collection_types"])
        self.assertNotIn("PROCUREMENT_DISCOVERY", result["collection_types"])

    def test_supplier_matching_and_partnerability_can_be_hybrid(self) -> None:
        result = self._triage(
            "Rank suitable international OEMs for a Bangladesh Coast Guard coastal patrol vessel opportunity and assess who can partner with us."
        )
        self.assertEqual("HYBRID", result["collection_mode"])
        self.assertIn("SUPPLIER_LANDSCAPE", result["collection_types"])
        self.assertIn("PARTNERABILITY", result["collection_types"])
        self.assertIn("OPPORTUNITY_MATCHING", result["collection_types"])

    def test_live_tender_supplier_recovery_enters_rapid_tender_mode(self) -> None:
        result = self._triage(
            "A Bangladesh Coast Guard patrol vessel tender is published and closes in 7 days; find eligible international OEMs."
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("RAPID_TENDER", result["collection_types"])
        self.assertIn("PROCUREMENT_DISCOVERY", result["collection_types"])
        self.assertIn("SUPPLIER_LANDSCAPE", result["collection_types"])
        self.assertEqual("C3_OPPORTUNITY", result["collection_depth"])

    def test_expansion_discovery_covers_follow_on_work(self) -> None:
        result = self._triage(
            "Find follow-on upgrades, spares and training opportunities from the existing Bangladesh Navy simulator project."
        )
        self.assertEqual("ARGUS_COLLECTION", result["collection_mode"])
        self.assertIn("EXPANSION_DISCOVERY", result["collection_types"])
        self.assertIn("INSTALLED_BASE", result["collection_types"])

    def test_preprocurement_opportunity_does_not_require_procurement_capability(self) -> None:
        plan = plan_canonical_capabilities(
            "What capability gaps could Bangladesh Coast Guard address with foreign technology?",
            task_classes=("RESEARCH",),
            collection_mode="ARGUS_COLLECTION",
            collection_types=("NEED_GAP", "BUYER_REQUIREMENT", "OPPORTUNITY_DISCOVERY"),
        )
        self.assertIn("argus.collection", plan["specialist"])
        self.assertNotIn("atlas.procurement-intelligence", plan["routed"])

    def test_rapid_tender_retains_procurement_capability(self) -> None:
        plan = plan_canonical_capabilities(
            "A tender is published and closes in 7 days; find eligible OEMs",
            task_classes=("RESEARCH",),
            collection_mode="ARGUS_COLLECTION",
            collection_types=("RAPID_TENDER", "PROCUREMENT_DISCOVERY", "SUPPLIER_LANDSCAPE"),
        )
        self.assertIn("atlas.procurement-intelligence", plan["routed"])
        self.assertIn("argus.collection", plan["specialist"])

    def test_argus_registry_pins_v3_candidate_and_unchanged_activation_contract(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text(encoding="utf-8"))
        method = next(item for item in registry["items"] if item["id"] == "domain-method.argus-intelligence")
        self.assertEqual("3.0.0-rc.1", method["version"])
        self.assertEqual("965ae0ddf885adf3dd2b9adfccae46b6b011227b", method["source_commit"])
        self.assertEqual("3.0.0", method["contract_version"])
        self.assertEqual(
            "sha256:5b082a12c6f0b469cba274a0e43e29032e349e3d377cf6d12ffa58762e8cb307",
            method["contract_sha256"],
        )
        self.assertIn("government_commercial_opportunity_intelligence", method["capabilities"])

    def test_atlas_candidate_advances_to_rc7_r11(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        ai_manifest = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        self.assertEqual("2.0.2-rc.7", manifest["product"]["version"])
        self.assertEqual("atlas-bootstrap-2026-10-22-r11", manifest["execution"]["control_revision"])
        self.assertEqual("2.0.2-rc.7", ai_manifest["product_version"])
        self.assertEqual("atlas-bootstrap-2026-10-22-r11", ai_manifest["control_revision"])


if __name__ == "__main__":
    unittest.main()
