from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class AccessAsiaSystemOfRecordTests(unittest.TestCase):
    def test_system_registry_defines_one_owner_per_information_class(self) -> None:
        path = ROOT / "integrations" / "access-asia" / "system-of-record.yaml"
        self.assertTrue(path.exists())
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertEqual("pointers_not_copies", data["principle"])
        self.assertEqual("canonical_crm", data["systems"]["hubspot"]["role"])
        self.assertEqual("canonical_document_and_working_file_store", data["systems"]["sharepoint"]["role"])
        self.assertEqual("canonical_structured_intelligence", data["systems"]["argus_github"]["role"])
        self.assertEqual("execution_and_persistence_governance", data["systems"]["atlas_github"]["role"])

    def test_persistence_router_is_deterministic(self) -> None:
        data = yaml.safe_load((ROOT / "integrations" / "access-asia" / "system-of-record.yaml").read_text(encoding="utf-8"))
        routes = data["persistence_routing"]
        expected = {
            "CRM_COMPANY": "HUBSPOT",
            "CRM_CONTACT": "HUBSPOT",
            "CRM_RELATIONSHIP": "HUBSPOT",
            "CRM_DEAL": "HUBSPOT",
            "SOURCE_DOCUMENT": "SHAREPOINT",
            "WORKING_DOCUMENT": "SHAREPOINT",
            "OPPORTUNITY_FOLDER": "SHAREPOINT",
            "PROJECT_DOCUMENT": "SHAREPOINT",
            "ARGUS_INTELLIGENCE": "ARGUS_GITHUB",
            "ARGUS_OPPORTUNITY": "ARGUS_GITHUB",
            "ARGUS_EVENT": "ARGUS_GITHUB",
            "ARGUS_MATCH": "ARGUS_GITHUB",
            "ARGUS_EVIDENCE_REFERENCE": "ARGUS_GITHUB",
            "ATLAS_POLICY": "ATLAS_GITHUB",
            "ATLAS_RUNTIME": "ATLAS_GITHUB",
            "ATLAS_REGISTRY": "ATLAS_GITHUB",
        }
        for information_class, target in expected.items():
            self.assertEqual(target, routes[information_class])

    def test_public_git_policy_excludes_external_native_ids_and_tokens(self) -> None:
        data = yaml.safe_load((ROOT / "integrations" / "access-asia" / "system-of-record.yaml").read_text(encoding="utf-8"))
        blocked = set(data["security"]["never_commit"])
        self.assertIn("sharepoint_sharing_tokens", blocked)
        self.assertIn("sharepoint_drive_ids", blocked)
        self.assertIn("sharepoint_item_ids", blocked)
        self.assertIn("hubspot_native_record_ids", blocked)
        self.assertEqual("resolve_at_runtime", data["security"]["native_external_ids"])

    def test_sharepoint_logical_locator_is_registered_without_native_item_ids(self) -> None:
        data = yaml.safe_load((ROOT / "integrations" / "access-asia" / "system-of-record.yaml").read_text(encoding="utf-8"))
        sharepoint = data["systems"]["sharepoint"]
        self.assertEqual("accessasiaccl.sharepoint.com", sharepoint["hostname"])
        self.assertEqual("/sites/accessasia", sharepoint["site_path"])
        self.assertEqual("General/Business Intelligence", sharepoint["business_intelligence_root"])
        self.assertTrue(sharepoint["native_item_id_storage_in_public_git"] == "prohibited")


if __name__ == "__main__":
    unittest.main()
