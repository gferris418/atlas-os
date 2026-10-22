from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CLASSIFICATION = ROOT / "registries" / "classification"

EXPECTED_FAMILIES = {
    "DOMAIN",
    "SECTOR",
    "INDUSTRY",
    "ECONOMIC_ACTIVITY",
    "PRODUCT",
    "CAPABILITY",
    "PROCUREMENT_CATEGORY",
    "TRADE_CLASSIFICATION",
    "OCCUPATION",
    "GEOGRAPHY",
    "COMPLIANCE_REGULATORY",
}
EXPECTED_SCHEMAS = {
    "schemas/classification-standard.schema.json",
    "schemas/classification-entry.schema.json",
    "schemas/classification-crosswalk.schema.json",
}
LIFECYCLES = {"DISCOVERED", "CANDIDATE", "VERIFIED", "ACTIVE", "SUPERSEDED", "ARCHIVED"}
EVIDENCE_STATUSES = {"CONFIRMED", "PROBABLE", "POSSIBLE", "DISPUTED", "UNVERIFIED", "STALE"}
CROSSWALK_RELATIONSHIPS = {"EXACT", "CLOSE", "BROADER", "NARROWER", "RELATED", "CANDIDATE"}


class ClassificationRegistryConformanceTests(unittest.TestCase):
    def test_classification_contract_files_exist(self) -> None:
        expected = [
            ROOT / "schemas" / "classification-standard.schema.json",
            ROOT / "schemas" / "classification-entry.schema.json",
            ROOT / "schemas" / "classification-crosswalk.schema.json",
            CLASSIFICATION / "families.yaml",
            CLASSIFICATION / "authorities.yaml",
        ]
        missing = [str(path.relative_to(ROOT)) for path in expected if not path.is_file()]
        self.assertEqual([], missing)

    def test_manifest_declares_classification_contracts(self) -> None:
        ai = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        self.assertTrue(EXPECTED_SCHEMAS.issubset(set(ai["machine_contracts"])))
        self.assertIn("registries/classification", manifest["registries"])

    def test_approved_families_are_unique_and_complete(self) -> None:
        path = CLASSIFICATION / "families.yaml"
        if not path.is_file():
            self.fail("classification families registry is missing")
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        families = payload["families"]
        ids = [entry["id"] for entry in families]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(EXPECTED_FAMILIES, set(ids))

    def test_authorities_have_unique_ids_names_and_sources(self) -> None:
        path = CLASSIFICATION / "authorities.yaml"
        if not path.is_file():
            self.fail("classification authorities registry is missing")
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        authorities = payload["authorities"]
        ids = [entry["id"] for entry in authorities]
        self.assertEqual(len(ids), len(set(ids)))
        for authority in authorities:
            self.assertTrue(authority["official_name"].strip())
            self.assertTrue(authority["source_url"].startswith("https://"))

    def test_catalogue_update_sources_and_crosswalk_files_exist(self) -> None:
        expected = [
            CLASSIFICATION / "standards.yaml",
            CLASSIFICATION / "update-sources.yaml",
            CLASSIFICATION / "crosswalks.yaml",
        ]
        missing = [str(path.relative_to(ROOT)) for path in expected if not path.is_file()]
        self.assertEqual([], missing)

    def test_standards_have_unique_ids_versions_and_valid_references(self) -> None:
        path = CLASSIFICATION / "standards.yaml"
        if not path.is_file():
            self.fail("classification standards catalogue is missing")

        standards = yaml.safe_load(path.read_text(encoding="utf-8"))["standards"]
        family_ids = {
            entry["id"]
            for entry in yaml.safe_load((CLASSIFICATION / "families.yaml").read_text(encoding="utf-8"))["families"]
        }
        authority_ids = {
            entry["id"]
            for entry in yaml.safe_load((CLASSIFICATION / "authorities.yaml").read_text(encoding="utf-8"))["authorities"]
        }

        standard_ids = [standard["standard_id"] for standard in standards]
        self.assertEqual(len(standard_ids), len(set(standard_ids)))

        version_ids: list[str] = []
        versions_by_id: dict[str, dict] = {}
        for standard in standards:
            self.assertIn(standard["family_id"], family_ids)
            self.assertIn(standard["authority_id"], authority_ids)
            self.assertTrue(standard["official_name"].strip())
            self.assertTrue(standard["abbreviation"].strip())
            self.assertTrue(standard["jurisdiction"].strip())
            for version in standard["versions"]:
                version_id = version["version_id"]
                version_ids.append(version_id)
                versions_by_id[version_id] = version
                self.assertIn(version["lifecycle"], LIFECYCLES)
                self.assertIn(version["evidence_status"], EVIDENCE_STATUSES)
                self.assertTrue(version["source_url"].startswith("https://"))
                if version["lifecycle"] == "ACTIVE":
                    self.assertEqual("CONFIRMED", version["evidence_status"])
                if version["dataset_storage"] == "FULL_DATASET":
                    self.assertEqual("PERMITTED", version["redistribution_status"])

        self.assertEqual(len(version_ids), len(set(version_ids)))
        for version in versions_by_id.values():
            supersedes = version.get("supersedes_version_id")
            if supersedes:
                self.assertIn(supersedes, versions_by_id)
                self.assertNotEqual(version["version_id"], supersedes)

    def test_update_sources_are_unique_and_authoritative(self) -> None:
        path = CLASSIFICATION / "update-sources.yaml"
        if not path.is_file():
            self.fail("classification update-source registry is missing")
        sources = yaml.safe_load(path.read_text(encoding="utf-8"))["update_sources"]
        ids = [source["id"] for source in sources]
        self.assertEqual(len(ids), len(set(ids)))
        for source in sources:
            self.assertTrue(source["url"].startswith("https://"))
            self.assertEqual("AUTHORITATIVE", source["source_class"])

    def test_crosswalk_relationships_are_explicit_and_directional(self) -> None:
        path = CLASSIFICATION / "crosswalks.yaml"
        if not path.is_file():
            self.fail("classification crosswalk registry is missing")
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["directional"])
        self.assertTrue(payload["candidate_is_not_canonical_equivalence"])
        ids: list[str] = []
        for crosswalk in payload["crosswalks"]:
            ids.append(crosswalk["crosswalk_id"])
            self.assertIn(crosswalk["relationship"], CROSSWALK_RELATIONSHIPS)
            self.assertIn(crosswalk["evidence_status"], EVIDENCE_STATUSES)
            self.assertTrue(crosswalk["source_url"].startswith("https://"))
        self.assertEqual(len(ids), len(set(ids)))

    def test_core_persistence_distinguishes_reference_operational_document_and_crm_workloads(self) -> None:
        persistence = yaml.safe_load((ROOT / "spec/persistence.yaml").read_text(encoding="utf-8"))
        workload_classes = persistence["contract"]["workload_classes"]
        self.assertEqual(
            {"VERSIONED_REFERENCE_DATA", "OPERATIONAL_RELATIONAL_STATE", "DOCUMENT_CONTENT", "CRM_STATE"},
            set(workload_classes),
        )
        self.assertEqual("reviewed_versioned", workload_classes["VERSIONED_REFERENCE_DATA"]["mutation_model"])
        self.assertEqual("transactional", workload_classes["OPERATIONAL_RELATIONAL_STATE"]["mutation_model"])
        self.assertNotIn("SHAREPOINT", str(persistence).upper())

    def test_argus_may_propose_but_cannot_promote_classification_state(self) -> None:
        argus = yaml.safe_load((ROOT / "integrations/argus.yaml").read_text(encoding="utf-8"))
        allowed = set(argus["autonomy_within_mission"]["may"])
        prohibited = set(argus["autonomy_within_mission"]["may_not"])
        self.assertIn("propose_classification_standards_and_crosswalks", allowed)
        self.assertIn("promote_classification_candidate_to_canonical", prohibited)
        self.assertIn("persist_canonical_classification_state_without_ATLAS_authorization", prohibited)


if __name__ == "__main__":
    unittest.main()
