from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative: str) -> dict:
    with (ROOT / relative).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{relative} must contain a mapping")
    return value


class ExpandedAtlasArchitectureConformance(unittest.TestCase):
    EXPECTED_ARCHITECTURE = {
        "mission_control": "spec/mission-control.yaml",
        "control_plane": "spec/control-plane.yaml",
        "collection_routing": "spec/collection-routing.yaml",
        "domain_context_services": "spec/domain-context-services.yaml",
        "domain_intelligence": "spec/domain-intelligence.yaml",
        "observability": "spec/observability.yaml",
        "dashboard": "spec/dashboard.yaml",
    }
    ACTIVE_AUTHORITIES = {
        "mission_control",
        "control_plane",
        "collection_routing",
        "domain_context_services",
        "observability",
        "dashboard",
    }

    def test_product_manifest_declares_expanded_architecture_authorities(self) -> None:
        manifest = load_yaml("atlas-os.yaml")
        self.assertIn("architecture", manifest)
        self.assertEqual(self.EXPECTED_ARCHITECTURE, manifest["architecture"])

    def test_ai_manifest_exposes_same_architecture_authorities(self) -> None:
        ai_manifest = load_yaml("atlas-ai.yaml")
        authority = ai_manifest.get("authority", {})
        self.assertIn("architecture", authority)
        self.assertEqual(self.EXPECTED_ARCHITECTURE, authority["architecture"])

    def test_canonical_architecture_specs_are_active_normative_and_machine_authoritative(self) -> None:
        ai_manifest = load_yaml("atlas-ai.yaml")
        machine_contracts = set(ai_manifest.get("machine_contracts", []))
        for name in self.ACTIVE_AUTHORITIES:
            relative = self.EXPECTED_ARCHITECTURE[name]
            with self.subTest(authority=name):
                path = ROOT / relative
                self.assertTrue(path.is_file(), relative)
                record = load_yaml(relative)
                self.assertTrue(record.get("normative"), relative)
                self.assertEqual("active", record.get("status"), relative)
                self.assertIn(relative, machine_contracts)

    def test_domain_intelligence_is_compatibility_alias_not_machine_authority(self) -> None:
        ai_manifest = load_yaml("atlas-ai.yaml")
        machine_contracts = set(ai_manifest.get("machine_contracts", []))
        relative = self.EXPECTED_ARCHITECTURE["domain_intelligence"]
        record = load_yaml(relative)
        self.assertTrue(record.get("normative"), relative)
        self.assertEqual("deprecated", record.get("status"), relative)
        self.assertEqual(
            "spec/domain-context-services.yaml",
            record["contract"]["canonical_replacement"],
        )
        self.assertNotIn(relative, machine_contracts)

    def test_argus_collection_is_nested_under_atlas_control_plane(self) -> None:
        collection = load_yaml("spec/collection-routing.yaml")["contract"]
        control = load_yaml("spec/control-plane.yaml")["contract"]
        self.assertEqual("ATLAS_CONTROL_PLANE", collection["owner"])
        self.assertEqual("intelligence_collection", collection["argus_capability"])
        self.assertIn("collection_need_decision", control["owns"])
        self.assertIn("final_delivery", collection["atlas_retains"])
        self.assertIn("collection_packaging", collection["argus_does"])


if __name__ == "__main__":
    unittest.main()
