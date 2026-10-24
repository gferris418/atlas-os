import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "atlas-os" / "SKILL.md"
CONTRACT = ROOT / "spec" / "persistence.yaml"


class SharePointPersistenceContractTests(unittest.TestCase):
    def test_canonical_contract_routes_atlas_and_argus_outputs(self):
        self.assertTrue(CONTRACT.is_file(), "missing canonical persistence contract")
        document = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        contract = document["contract"]
        sharepoint = contract["canonical_sharepoint"]

        self.assertEqual("3.0.0", document["version"])
        self.assertEqual("ATLAS_CONTROL_PLANE", contract["owner"])
        self.assertEqual("accessasiaccl.sharepoint.com", sharepoint["hostname"])
        self.assertEqual("/sites/accessasia", sharepoint["site_path"])
        self.assertEqual("General/Chats", sharepoint["roots"]["atlas_generic"]["path"])
        self.assertEqual(
            "General/Business Intelligence",
            sharepoint["roots"]["argus_intelligence"]["path"],
        )
        self.assertEqual("atlas_generic", sharepoint["routing"]["generic_chat"])
        self.assertEqual("argus_intelligence", sharepoint["routing"]["intelligence_collection"])
        self.assertTrue(sharepoint["rules"]["single_canonical_copy"])
        self.assertTrue(sharepoint["rules"]["durable_write_receipt_required"])
        self.assertTrue(sharepoint["authorization"]["canonical_roots_preauthorized"])

    def test_skill_bootstraps_and_enforces_persistence_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("spec/persistence.yaml", text)
        self.assertIn("General/Chats", text)
        self.assertIn("General/Business Intelligence", text)
        self.assertIn("PERSISTENCE_PENDING", text)
        self.assertIn("verifiable durable-write receipt", text)


if __name__ == "__main__":
    unittest.main()
