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


if __name__ == "__main__":
    unittest.main()
