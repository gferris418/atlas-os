from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.validate import validate as validate_repository

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "registries" / "classification"
CATALOGUES = BASE / "catalogues"

EXPECTED = {
    "economic-activity.yaml": "ECONOMIC_ACTIVITY",
    "industry.yaml": "INDUSTRY",
    "product.yaml": "PRODUCT",
    "sector.yaml": "SECTOR",
    "domain.yaml": "DOMAIN",
    "capability.yaml": "CAPABILITY",
    "technology.yaml": "TECHNOLOGY",
}
SOURCE_MODES = {"ATLAS_OWNED", "REMOTE_AUTHORITATIVE", "METADATA_ONLY"}


class ClassificationCatalogueConformanceTests(unittest.TestCase):
    def test_expected_catalogue_descriptors_exist(self) -> None:
        actual = {path.name for path in CATALOGUES.glob("*.yaml")}
        self.assertEqual(set(EXPECTED), actual)

    def test_catalogue_descriptors_have_unique_ids_and_governed_sources(self) -> None:
        ids: list[str] = []
        for filename, family_id in EXPECTED.items():
            payload = yaml.safe_load((CATALOGUES / filename).read_text(encoding="utf-8"))
            ids.append(payload["catalogue_id"])
            self.assertEqual(family_id, payload["family_id"])
            self.assertTrue(payload["version"])
            self.assertTrue(payload["owner"])
            self.assertIn(payload["source_mode"], SOURCE_MODES)
            self.assertIn(payload["lifecycle"], {"CANDIDATE", "VERIFIED", "ACTIVE", "SUPERSEDED", "ARCHIVED"})
            self.assertIn(payload["redistribution_status"], {"PERMITTED", "RESTRICTED", "UNKNOWN", "NOT_APPLICABLE"})
            if payload["source_mode"] == "ATLAS_OWNED":
                self.assertEqual("ATLAS", payload["owner"])
                self.assertEqual("ATLAS", payload["authority_id"])
                self.assertTrue(payload["source_standard_id"].startswith("STD-ATLAS-"))
                self.assertTrue(payload["source_version_id"].startswith("VER-ATLAS-"))
            else:
                self.assertTrue(payload["source_standard_id"])
                self.assertTrue(payload["source_version_id"])
                self.assertTrue(payload["source_url"].startswith("https://"))
        self.assertEqual(len(ids), len(set(ids)))

    def test_atlas_authority_and_owned_standards_exist(self) -> None:
        authorities = yaml.safe_load((BASE / "authorities.yaml").read_text(encoding="utf-8"))["authorities"]
        self.assertIn("ATLAS", {record["id"] for record in authorities})
        standards = yaml.safe_load((BASE / "standards.yaml").read_text(encoding="utf-8"))["standards"]
        ids = {record["standard_id"] for record in standards}
        self.assertTrue(
            {
                "STD-ATLAS-SECTOR",
                "STD-ATLAS-INDUSTRY",
                "STD-ATLAS-DOMAIN",
                "STD-ATLAS-CAPABILITY",
                "STD-ATLAS-TECHNOLOGY",
            }.issubset(ids)
        )

    def test_remote_catalogues_use_existing_standard_versions(self) -> None:
        standards = yaml.safe_load((BASE / "standards.yaml").read_text(encoding="utf-8"))["standards"]
        version_owners = {
            version["version_id"]: standard["standard_id"]
            for standard in standards
            for version in standard["versions"]
        }
        for filename in ("economic-activity.yaml", "product.yaml"):
            payload = yaml.safe_load((CATALOGUES / filename).read_text(encoding="utf-8"))
            self.assertEqual(payload["source_standard_id"], version_owners[payload["source_version_id"]])

    def test_validator_rejects_duplicate_item_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "atlas-os"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = root / "registries" / "classification" / "catalogues" / "sector.yaml"
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            item = {
                "atlas_classification_id": "SECTOR-TEST",
                "family_id": "SECTOR",
                "preferred_label": "Test",
                "definition": "Test sector.",
                "source_standard_id": payload["source_standard_id"],
                "source_version_id": payload["source_version_id"],
                "source_code": "TEST",
                "source_label": "Test",
                "level": "SECTOR",
                "parent_id": None,
                "hierarchy_path": [],
                "jurisdiction": "ATLAS",
                "authority_id": "ATLAS",
                "source_url": "https://github.com/gferris418/atlas-os",
                "lifecycle": "ACTIVE",
                "evidence_status": "CONFIRMED",
                "redistribution_status": "NOT_APPLICABLE",
            }
            payload["items"] = [item, dict(item)]
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors = validate_repository(root)
        self.assertIn("duplicate classification item ID in CAT-ATLAS-SECTOR: SECTOR-TEST", errors)

    def test_validator_rejects_unknown_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "atlas-os"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = root / "registries" / "classification" / "catalogues" / "sector.yaml"
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            payload["items"] = [
                {
                    "atlas_classification_id": "SECTOR-TEST-CHILD",
                    "family_id": "SECTOR",
                    "preferred_label": "Child",
                    "definition": "Test child sector.",
                    "source_standard_id": payload["source_standard_id"],
                    "source_version_id": payload["source_version_id"],
                    "source_code": "TEST-CHILD",
                    "source_label": "Child",
                    "level": "SUBSECTOR",
                    "parent_id": "SECTOR-MISSING",
                    "hierarchy_path": ["SECTOR-MISSING"],
                    "jurisdiction": "ATLAS",
                    "authority_id": "ATLAS",
                    "source_url": "https://github.com/gferris418/atlas-os",
                    "lifecycle": "ACTIVE",
                    "evidence_status": "CONFIRMED",
                    "redistribution_status": "NOT_APPLICABLE",
                }
            ]
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors = validate_repository(root)
        self.assertIn("unknown classification parent in CAT-ATLAS-SECTOR: SECTOR-MISSING", errors)


if __name__ == "__main__":
    unittest.main()
