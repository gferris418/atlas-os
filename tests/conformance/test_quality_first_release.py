from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class QualityFirstReleaseConformanceTests(unittest.TestCase):
    def test_product_and_plugin_versions_are_3_0_3(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        ai = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        governance = yaml.safe_load((ROOT / "governance.yaml").read_text(encoding="utf-8"))
        plugin = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        chatgpt = yaml.safe_load((ROOT / "integrations/chatgpt.yaml").read_text(encoding="utf-8"))
        skill = (ROOT / "skills/atlas-os/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual("3.0.3", manifest["product"]["version"])
        self.assertEqual("3.0.3", ai["product_version"])
        self.assertEqual("3.0.3", governance["version"])
        self.assertEqual("3.0.3", plugin["version"])
        self.assertEqual("3.0.3", chatgpt["version"])
        self.assertIn("version: 3.0.3", skill)

    def test_quality_and_persistence_contracts_are_machine_discoverable(self) -> None:
        ai = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        for path in (
            "spec/quality-governance.yaml",
            "spec/chat-event-persistence.yaml",
            "spec/performance-telemetry.yaml",
        ):
            self.assertIn(path, ai["discovery_order"])
            self.assertIn(path, ai["machine_contracts"])

    def test_performance_telemetry_cannot_drive_quality_tier_selection(self) -> None:
        telemetry = yaml.safe_load((ROOT / "spec/performance-telemetry.yaml").read_text(encoding="utf-8"))
        contract = telemetry["contract"]
        self.assertTrue(contract["normative"])
        self.assertFalse(contract["may_select_or_lower_quality_tier"])
        self.assertIn("latency_ms", contract["metrics"])
        self.assertIn("tool_calls", contract["metrics"])
        self.assertIn("verified_state_reuse", contract["metrics"])
        self.assertIn("duplicate_retrieval_avoided", contract["metrics"])
        self.assertIn("persistence_latency_ms", contract["metrics"])

    def test_fast_text_and_quality_first_rules_are_packaged_in_skill(self) -> None:
        skill = (ROOT / "skills/atlas-os/SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("quality", skill)
        self.assertIn("q0", skill)
        self.assertIn("q5", skill)
        self.assertIn("fast_text", skill)
        self.assertIn("presentation", skill)
        self.assertIn("completed user-visible prompt", skill)
        self.assertIn("hidden chain-of-thought", skill)


if __name__ == "__main__":
    unittest.main()
