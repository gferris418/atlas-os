from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "registries" / "classification"
SOURCES = BASE / "catalogues" / "sources"

EXPECTED = {
    "isic-rev5.yaml": ("STD-UN-ISIC", "VER-UN-ISIC-REV5", "UNSD"),
    "cpc-3.0.yaml": ("STD-UN-CPC", "VER-UN-CPC-3.0", "UNSD"),
    "nace-rev2.1.yaml": ("STD-EU-NACE", "VER-EU-NACE-REV2.1", "EUROSTAT"),
    "naics-2022.yaml": ("STD-US-NAICS", "VER-US-NAICS-2022", "US_CENSUS"),
    "cpv-2008.yaml": ("STD-EU-CPV", "VER-EU-CPV-2008", "EUROPEAN_COMMISSION"),
}


class ClassificationSourceDescriptorTests(unittest.TestCase):
    def test_expected_authoritative_source_descriptors_exist(self) -> None:
        self.assertEqual(set(EXPECTED), {path.name for path in SOURCES.glob("*.yaml")})

    def test_source_descriptors_are_version_bound_and_rights_aware(self) -> None:
        ids: list[str] = []
        for filename, (standard_id, version_id, authority_id) in EXPECTED.items():
            payload = yaml.safe_load((SOURCES / filename).read_text(encoding="utf-8"))
            ids.append(payload["source_descriptor_id"])
            self.assertEqual(standard_id, payload["standard_id"])
            self.assertEqual(version_id, payload["version_id"])
            self.assertEqual(authority_id, payload["authority_id"])
            self.assertTrue(payload["official_url"].startswith("https://"))
            self.assertIn(payload["retrieval_mode"], {"REMOTE_AUTHORITATIVE", "METADATA_ONLY"})
            self.assertIn(payload["redistribution_status"], {"PERMITTED", "RESTRICTED", "UNKNOWN"})
            self.assertIn(payload["dataset_storage"], {"NONE", "METADATA_ONLY", "PERMITTED_EXTRACT", "FULL_DATASET"})
            self.assertRegex(payload["last_verified_at"], r"^\d{4}-\d{2}-\d{2}$")
            if payload["dataset_storage"] == "FULL_DATASET":
                self.assertEqual("PERMITTED", payload["redistribution_status"])
            if payload["independently_verified"]:
                self.assertRegex(payload["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(payload["expected_counts"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_isic_rev5_structure_counts_and_digest_are_pinned(self) -> None:
        payload = yaml.safe_load((SOURCES / "isic-rev5.yaml").read_text(encoding="utf-8"))
        self.assertTrue(payload["independently_verified"])
        self.assertEqual(
            {"sections": 22, "divisions": 87, "groups": 258, "classes": 463, "total_nodes": 830},
            payload["expected_counts"],
        )
        self.assertEqual("fc408f57bd3a4f33c35a4f384ec0010283dd72774892c8d48ae1330a8caeb57f", payload["sha256"])

    def test_cpc_3_structure_count_and_digest_are_pinned(self) -> None:
        payload = yaml.safe_load((SOURCES / "cpc-3.0.yaml").read_text(encoding="utf-8"))
        self.assertTrue(payload["independently_verified"])
        self.assertEqual(4586, payload["expected_counts"]["total_nodes"])
        self.assertEqual("5cd2c1c4890dd6be16af48e9bb940fed48efff9865f39ff15edaa921da25fb7c", payload["sha256"])

    def test_unverified_descriptors_do_not_claim_digest_or_counts(self) -> None:
        for filename in ("nace-rev2.1.yaml", "naics-2022.yaml", "cpv-2008.yaml"):
            payload = yaml.safe_load((SOURCES / filename).read_text(encoding="utf-8"))
            if not payload["independently_verified"]:
                self.assertNotIn("sha256", payload)
                self.assertNotIn("expected_counts", payload)


if __name__ == "__main__":
    unittest.main()
