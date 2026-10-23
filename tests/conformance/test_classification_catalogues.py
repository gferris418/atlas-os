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
REQUIRED_IDS = {
    "sector.yaml": {
        "SECTOR-DEFENCE-SECURITY", "SECTOR-MARITIME", "SECTOR-TRANSPORT", "SECTOR-ENERGY",
        "SECTOR-INFRASTRUCTURE", "SECTOR-ICT-TELECOM", "SECTOR-HEALTHCARE",
        "SECTOR-WATER-ENVIRONMENT", "SECTOR-AGRICULTURE", "SECTOR-EDUCATION",
        "SECTOR-FINANCIAL-SERVICES", "SECTOR-PUBLIC-ADMINISTRATION",
    },
    "industry.yaml": {
        "INDUSTRY-SHIPBUILDING", "INDUSTRY-MARINE-EQUIPMENT", "INDUSTRY-DEFENCE-ELECTRONICS",
        "INDUSTRY-TELECOM-EQUIPMENT", "INDUSTRY-ENGINEERING-CONSULTING", "INDUSTRY-SOFTWARE",
        "INDUSTRY-CYBERSECURITY-SERVICES", "INDUSTRY-BATTERY-MANUFACTURING",
        "INDUSTRY-BRIDGE-COMPONENTS", "INDUSTRY-AEROSPACE", "INDUSTRY-RAIL-EQUIPMENT",
        "INDUSTRY-POWER-EQUIPMENT", "INDUSTRY-MEDICAL-DEVICES", "INDUSTRY-WATER-TREATMENT",
    },
    "domain.yaml": {
        "DOMAIN-MARITIME", "DOMAIN-C4ISR", "DOMAIN-PORTS", "DOMAIN-ENERGY",
        "DOMAIN-CIVIL-INFRASTRUCTURE", "DOMAIN-ICT-DIGITAL", "DOMAIN-SECURITY", "DOMAIN-HEALTHCARE",
    },
    "capability.yaml": {
        "CAP-MARITIME-SURVEILLANCE", "CAP-VESSEL-DETECTION", "CAP-VESSEL-IDENTIFICATION",
        "CAP-VESSEL-TRACKING", "CAP-MARITIME-DOMAIN-AWARENESS", "CAP-COMMAND-CONTROL",
        "CAP-COMMUNICATIONS", "CAP-PORT-AUTOMATION", "CAP-VESSEL-TRAFFIC-MANAGEMENT",
        "CAP-RENEWABLE-POWER", "CAP-GRID-STABILITY", "CAP-ENERGY-STORAGE",
        "CAP-BRIDGE-ENGINEERING", "CAP-STRUCTURAL-MONITORING",
    },
    "technology.yaml": {
        "TECH-AI", "TECH-AI-ML", "TECH-AI-COMPUTER-VISION", "TECH-AI-NLP", "TECH-AI-GENERATIVE",
        "TECH-RADAR", "TECH-EO-IR", "TECH-LIDAR", "TECH-SONAR", "TECH-GNSS", "TECH-INS", "TECH-PNT",
        "TECH-RF", "TECH-SATCOM", "TECH-5G", "TECH-TACTICAL-DATA-LINK", "TECH-DIESEL-PROPULSION",
        "TECH-GAS-TURBINE", "TECH-ELECTRIC-PROPULSION", "TECH-HYBRID-PROPULSION", "TECH-SIMULATION",
        "TECH-DIGITAL-TWIN", "TECH-CYBERSECURITY", "TECH-IOT", "TECH-ROBOTICS", "TECH-CLOUD",
        "TECH-EDGE", "TECH-BATTERY", "TECH-HYDROGEN", "TECH-DLT", "TECH-QUANTUM",
    },
}


class ClassificationCatalogueConformanceTests(unittest.TestCase):
    def test_expected_catalogue_descriptors_exist(self) -> None:
        self.assertEqual(set(EXPECTED), {path.name for path in CATALOGUES.glob("*.yaml")})

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
        self.assertTrue({"STD-ATLAS-SECTOR", "STD-ATLAS-INDUSTRY", "STD-ATLAS-DOMAIN", "STD-ATLAS-CAPABILITY", "STD-ATLAS-TECHNOLOGY"}.issubset(ids))

    def test_remote_catalogues_use_existing_standard_versions(self) -> None:
        standards = yaml.safe_load((BASE / "standards.yaml").read_text(encoding="utf-8"))["standards"]
        version_owners = {version["version_id"]: standard["standard_id"] for standard in standards for version in standard["versions"]}
        for filename in ("economic-activity.yaml", "product.yaml"):
            payload = yaml.safe_load((CATALOGUES / filename).read_text(encoding="utf-8"))
            self.assertEqual(payload["source_standard_id"], version_owners[payload["source_version_id"]])

    def test_atlas_owned_catalogues_have_required_seed_items(self) -> None:
        for filename, expected_ids in REQUIRED_IDS.items():
            payload = yaml.safe_load((CATALOGUES / filename).read_text(encoding="utf-8"))
            items = payload["items"]
            ids = {item["atlas_classification_id"] for item in items}
            self.assertTrue(expected_ids.issubset(ids), f"{filename}: {sorted(expected_ids - ids)}")
            for item in items:
                self.assertTrue(item["serial"])
                self.assertTrue(item["definition"])
                self.assertEqual(payload["family_id"], item["family_id"])

    def test_atlas_owned_serials_are_unique_and_hierarchical(self) -> None:
        for filename in REQUIRED_IDS:
            payload = yaml.safe_load((CATALOGUES / filename).read_text(encoding="utf-8"))
            items = payload["items"]
            serials = [item["serial"] for item in items]
            self.assertEqual(len(serials), len(set(serials)), filename)
            by_id = {item["atlas_classification_id"]: item for item in items}
            for item in items:
                parent_id = item.get("parent_id")
                if parent_id:
                    self.assertIn(parent_id, by_id)
                    self.assertTrue(item["serial"].startswith(by_id[parent_id]["serial"] + "."))

    def _test_item(self, payload: dict, *, item_id: str, parent_id: str | None, serial: str) -> dict:
        return {
            "atlas_classification_id": item_id,
            "serial": serial,
            "family_id": payload["family_id"],
            "preferred_label": "Test",
            "definition": "Test classification.",
            "source_standard_id": payload["source_standard_id"],
            "source_version_id": payload["source_version_id"],
            "source_code": "TEST",
            "source_label": "Test",
            "level": "TEST",
            "parent_id": parent_id,
            "hierarchy_path": [] if parent_id is None else [parent_id],
            "jurisdiction": "ATLAS",
            "authority_id": "ATLAS",
            "source_url": "https://github.com/gferris418/atlas-os",
            "lifecycle": "ACTIVE",
            "evidence_status": "CONFIRMED",
            "redistribution_status": "PERMITTED",
        }

    def test_validator_rejects_duplicate_item_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "atlas-os"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = root / "registries" / "classification" / "catalogues" / "sector.yaml"
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            item = self._test_item(payload, item_id="SECTOR-TEST", parent_id=None, serial="98")
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
            payload["items"] = [self._test_item(payload, item_id="SECTOR-TEST-CHILD", parent_id="SECTOR-MISSING", serial="99.01")]
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors = validate_repository(root)
        self.assertIn("unknown classification parent in CAT-ATLAS-SECTOR: SECTOR-MISSING", errors)

    def test_validator_rejects_duplicate_serials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "atlas-os"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = root / "registries" / "classification" / "catalogues" / "sector.yaml"
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            payload["items"] = [
                self._test_item(payload, item_id="SECTOR-TEST-A", parent_id=None, serial="98"),
                self._test_item(payload, item_id="SECTOR-TEST-B", parent_id=None, serial="98"),
            ]
            path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
            errors = validate_repository(root)
        self.assertIn("duplicate classification serial in CAT-ATLAS-SECTOR: 98", errors)


if __name__ == "__main__":
    unittest.main()
