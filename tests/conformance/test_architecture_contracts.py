from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative: str) -> dict:
    with (ROOT / relative).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{relative} must contain a mapping")
    return value


class FourPlaneArchitectureConformance(unittest.TestCase):
    EXPECTED_ARCHITECTURE = {
        "mission_control": "spec/mission-control.yaml",
        "control_plane": "spec/control-plane.yaml",
        "observability": "spec/observability.yaml",
        "domain_intelligence": "spec/domain-intelligence.yaml",
    }

    def test_product_manifest_declares_four_architecture_authorities(self) -> None:
        manifest = load_yaml("atlas-os.yaml")
        self.assertIn("architecture", manifest)
        self.assertEqual(self.EXPECTED_ARCHITECTURE, manifest["architecture"])

    def test_ai_manifest_exposes_same_architecture_authorities(self) -> None:
        ai_manifest = load_yaml("atlas-ai.yaml")
        authority = ai_manifest.get("authority", {})
        self.assertIn("architecture", authority)
        self.assertEqual(self.EXPECTED_ARCHITECTURE, authority["architecture"])

    def test_architecture_specs_are_normative_and_machine_discovered(self) -> None:
        ai_manifest = load_yaml("atlas-ai.yaml")
        machine_contracts = set(ai_manifest.get("machine_contracts", []))
        for name, relative in self.EXPECTED_ARCHITECTURE.items():
            with self.subTest(authority=name):
                path = ROOT / relative
                self.assertTrue(path.is_file(), relative)
                record = load_yaml(relative)
                self.assertTrue(record.get("normative"), relative)
                self.assertEqual("active", record.get("status"), relative)
                self.assertIn(relative, machine_contracts)


if __name__ == "__main__":
    unittest.main()
