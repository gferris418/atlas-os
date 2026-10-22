from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "integrations" / "access-asia.yaml"


class AccessAsiaDataOwnershipConformanceTests(unittest.TestCase):
    def test_canonical_commercial_graph_routes_to_sharepoint_sqlite(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        authority = profile["authority"]
        routing = profile["persistence_routing"]

        self.assertEqual("canonical_commercial_graph_and_argus_current_state", authority["sharepoint_sqlite"])
        self.assertEqual("crm_relationship_engagement_and_contactability", authority["hubspot"])

        for key in (
            "CANONICAL_ORGANIZATION",
            "CANONICAL_PRODUCT",
            "GOVERNMENT_PROJECT",
            "REQUIREMENT",
            "TENDER",
            "PX_OPPORTUNITY",
            "BID",
            "AWARD",
            "ACCESS_ASIA_PROJECT",
            "FINANCIAL_FACT",
        ):
            self.assertEqual("SHAREPOINT_SQLITE", routing[key])

    def test_crm_documents_and_code_keep_separate_authorities(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        routing = profile["persistence_routing"]

        self.assertEqual("HUBSPOT", routing["CRM_RELATIONSHIP"])
        self.assertEqual("HUBSPOT", routing["CRM_INTERACTION"])
        self.assertEqual("SHAREPOINT", routing["SOURCE_DOCUMENT"])
        self.assertEqual("SHAREPOINT", routing["FINANCIAL_EVIDENCE_DOCUMENT"])
        self.assertEqual("ARGUS_GITHUB", routing["ARGUS_SCHEMA_AND_IDENTITY_RULES"])
        self.assertEqual("ATLAS_GITHUB", routing["ATLAS_POLICY_AND_RUNTIME"])

    def test_classification_reference_and_operational_state_use_different_stores(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        routing = profile["persistence_routing"]
        for key in (
            "CLASSIFICATION_STANDARD",
            "CLASSIFICATION_AUTHORITY",
            "CLASSIFICATION_VERSION",
            "CLASSIFICATION_CROSSWALK",
            "CLASSIFICATION_UPDATE_SOURCE",
            "CLASSIFICATION_DATASET_METADATA",
        ):
            self.assertEqual("ATLAS_GITHUB", routing[key])
        self.assertEqual("SHAREPOINT_SQLITE", routing["OPERATIONAL_ENTITY_CLASSIFICATION"])
        self.assertEqual("SHAREPOINT", routing["CLASSIFICATION_SOURCE_DOCUMENT"])
        self.assertEqual("SHAREPOINT", routing["LARGE_OR_RESTRICTED_CLASSIFICATION_SOURCE_DOCUMENT"])

    def test_department_reporting_is_derived_not_separate_master_data(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        reporting = profile["reporting"]

        self.assertEqual("DERIVED_VIEWS", reporting["model"])
        self.assertFalse(reporting["department_master_databases"])
        self.assertEqual(
            {"MARKETING", "SALES", "BUSINESS_DEVELOPMENT", "OPERATIONS", "FINANCE", "MANAGEMENT"},
            set(reporting["departments"]),
        )


if __name__ == "__main__":
    unittest.main()
