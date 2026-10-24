import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "atlas-os" / "SKILL.md"
CORE = ROOT / "spec" / "persistence.yaml"
PROFILE = ROOT / "integrations" / "access-asia.yaml"


class SharePointPersistenceContractTests(unittest.TestCase):
    def test_access_asia_profile_routes_atlas_and_argus_outputs(self):
        self.assertTrue(CORE.is_file(), "missing core persistence contract")
        core = yaml.safe_load(CORE.read_text(encoding="utf-8"))
        self.assertEqual("ATLAS_CONTROL_PLANE", core["contract"]["owner"])
        self.assertNotIn("SHAREPOINT", str(core).upper())

        self.assertTrue(PROFILE.is_file(), "missing Access Asia deployment profile")
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        sharepoint = profile["canonical_sharepoint"]

        self.assertEqual("deployment_profile", profile["role"])
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
        self.assertIn("integrations/access-asia.yaml", text)
        self.assertIn("General/Chats", text)
        self.assertIn("General/Business Intelligence", text)
        self.assertIn("PERSISTENCE_PENDING", text)
        self.assertIn("verifiable durable-write receipt", text)


if __name__ == "__main__":
    unittest.main()
