import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "atlas-os" / "SKILL.md"
CONTRACT = ROOT / "spec" / "persistence.yaml"


class SharePointPersistenceContractTests(unittest.TestCase):
    def test_canonical_contract_routes_atlas_and_argus_outputs(self):
        self.assertTrue(CONTRACT.is_file(), "missing canonical persistence contract")
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))

        self.assertEqual("1.0.0", contract["version"])
        self.assertEqual("atlas-os", contract["authority"]["owner"])
        self.assertEqual("accessasiaccl.sharepoint.com", contract["sharepoint"]["hostname"])
        self.assertEqual("/sites/accessasia", contract["sharepoint"]["site_path"])
        self.assertEqual("General/Chats", contract["roots"]["atlas_generic"]["path"])
        self.assertEqual(
            "General/Business Intelligence",
            contract["roots"]["argus_intelligence"]["path"],
        )
        self.assertEqual("atlas_generic", contract["routing"]["generic_chat"])
        self.assertEqual("argus_intelligence", contract["routing"]["intelligence_collection"])
        self.assertTrue(contract["rules"]["single_canonical_copy"])
        self.assertTrue(contract["rules"]["durable_write_receipt_required"])
        self.assertTrue(contract["authorization"]["canonical_roots_preauthorized"])

    def test_skill_bootstraps_and_enforces_persistence_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("spec/persistence.yaml", text)
        self.assertIn("General/Chats", text)
        self.assertIn("General/Business Intelligence", text)
        self.assertIn("PERSISTENCE_PENDING", text)
        self.assertIn("verifiable durable-write receipt", text)


if __name__ == "__main__":
    unittest.main()
