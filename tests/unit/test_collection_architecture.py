from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class CollectionArchitectureTests(unittest.TestCase):
    def test_fixed_atlas_architecture_is_first_class(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        architecture = manifest["architecture"]
        self.assertEqual("spec/mission-control.yaml", architecture["mission_control"])
        self.assertEqual("spec/control-plane.yaml", architecture["control_plane"])
        self.assertEqual("spec/collection-routing.yaml", architecture["collection_routing"])
        self.assertEqual("spec/domain-context-services.yaml", architecture["domain_context_services"])
        self.assertEqual("spec/observability.yaml", architecture["observability"])
        self.assertEqual("spec/dashboard.yaml", architecture["dashboard"])

    def test_collection_gate_preserves_argus_boundary(self) -> None:
        spec = yaml.safe_load((ROOT / "spec/collection-routing.yaml").read_text(encoding="utf-8"))
        contract = spec["contract"]
        self.assertEqual("ATLAS_CONTROL_PLANE", contract["owner"])
        self.assertEqual(["NONE", "ATLAS_DIRECT", "ARGUS_COLLECTION", "HYBRID"], contract["modes"])
        self.assertEqual("intelligence_collection", contract["argus_capability"])
        self.assertIn("strategic_analysis", contract["atlas_retains"])
        self.assertIn("collection_packaging", contract["argus_does"])

    def test_argus_is_commit_pinned_collection_provider(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text(encoding="utf-8"))
        argus = registry["items"][0]
        self.assertEqual("3.0.0-rc.1", argus["version"])
        self.assertIn("intelligence_collection", argus["capabilities"])
        self.assertIn("government_commercial_opportunity_intelligence", argus["capabilities"])
        self.assertEqual("965ae0ddf885adf3dd2b9adfccae46b6b011227b", argus["source_commit"])
        self.assertEqual("3.0.0", argus["contract_version"])
        self.assertEqual("sha256:5b082a12c6f0b469cba274a0e43e29032e349e3d377cf6d12ffa58762e8cb307", argus["contract_sha256"])

    def test_collection_mission_schema_is_machine_readable(self) -> None:
        schema = json.loads((ROOT / "schemas/collection-mission.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(["ARGUS_COLLECTION", "HYBRID"], schema["properties"]["collection_mode"]["enum"])
        self.assertIn("collection_depth", schema["properties"])
        self.assertIn("stopping_rule", schema["required"])

    def test_economic_taxonomy_stack_uses_current_named_editions(self) -> None:
        registry = yaml.safe_load((ROOT / "registries/taxonomies.yaml").read_text(encoding="utf-8"))
        versions = {item["id"]: str(item["version"]) for item in registry["items"]}
        self.assertEqual("Rev. 5", versions["taxonomy.un-isic"])
        self.assertEqual("2020", versions["taxonomy.bd-bsic"])
        self.assertEqual("Rev. 2.1", versions["taxonomy.eu-nace"])
        self.assertEqual("2022", versions["taxonomy.naics"])
        self.assertEqual("3.0", versions["taxonomy.un-cpc"])
        self.assertEqual("2011", versions["taxonomy.bd-bcpc"])
        self.assertEqual("2.2", versions["taxonomy.eu-cpa"])
        self.assertEqual("2008", versions["taxonomy.eu-cpv"])
        self.assertEqual("2022", versions["taxonomy.wco-hs"])
        self.assertEqual("FY 2026-2027", versions["taxonomy.bd-customs-tariff"])


if __name__ == "__main__":
    unittest.main()
