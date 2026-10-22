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

        self.assertEqual("governed_authority_by_information_class", data["principle"])
        self.assertEqual("canonical_crm", data["systems"]["hubspot"]["role"])
        self.assertEqual(
            "canonical_document_working_file_and_argus_operational_database_store",
            data["systems"]["sharepoint"]["role"],
        )
        self.assertEqual(
            "argus_schema_governance_code_migrations_and_versioned_release_snapshots",
            data["systems"]["argus_github"]["role"],
        )
        self.assertEqual(
            "canonical_current_mutable_argus_operational_structured_state",
            data["systems"]["argus_sharepoint_sqlite"]["role"],
        )
        self.assertEqual("execution_and_persistence_governance", data["systems"]["atlas_github"]["role"])

    def test_persistence_router_is_deterministic(self) -> None:
        data = yaml.safe_load((ROOT / "integrations" / "access-asia" / "system-of-record.yaml").read_text(encoding="utf-8"))
        routes = data["persistence_routing"]
        expected = {
            "CRM_COMPANY": "HUBSPOT",
            "CRM_CONTACT": "HUBSPOT",
            "CRM_RELATIONSHIP": "HUBSPOT",
            "CRM_DEAL": "HUBSPOT",
            "CRM_INTERACTION": "HUBSPOT",
            "SOURCE_DOCUMENT": "SHAREPOINT",
            "WORKING_DOCUMENT": "SHAREPOINT",
            "OPPORTUNITY_FOLDER": "SHAREPOINT",
            "PROJECT_DOCUMENT": "SHAREPOINT",
            "ARGUS_CURRENT_STRUCTURED_STATE": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_CANONICAL_OBJECT": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_OPPORTUNITY": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_EVENT": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_OBSERVATION": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_MATCH_CURRENT_STATE": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_EVIDENCE_REFERENCE": "ARGUS_SHAREPOINT_SQLITE",
            "ARGUS_SCHEMA": "ARGUS_GITHUB",
            "ARGUS_IDENTITY_RULES": "ARGUS_GITHUB",
            "ARGUS_MIGRATION": "ARGUS_GITHUB",
            "ARGUS_RELEASE_SNAPSHOT": "ARGUS_GITHUB",
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

    def test_sharepoint_logical_locator_and_operational_database_are_registered_without_native_item_ids(self) -> None:
        data = yaml.safe_load((ROOT / "integrations" / "access-asia" / "system-of-record.yaml").read_text(encoding="utf-8"))
        sharepoint = data["systems"]["sharepoint"]
        operational = data["systems"]["argus_sharepoint_sqlite"]
        self.assertEqual("accessasiaccl.sharepoint.com", sharepoint["hostname"])
        self.assertEqual("/sites/accessasia", sharepoint["site_path"])
        self.assertEqual("General/Business Intelligence", sharepoint["business_intelligence_root"])
        self.assertEqual(
            "General/Business Intelligence/30_OPERATIONS/ARGUS_Master_Registry.sqlite",
            operational["logical_path"],
        )
        self.assertEqual("prohibited", sharepoint["native_item_id_storage_in_public_git"])
        self.assertEqual("single_writer_fetch_latest_modify_transactionally_verify_replace", operational["mutation_model"])


if __name__ == "__main__":
    unittest.main()
