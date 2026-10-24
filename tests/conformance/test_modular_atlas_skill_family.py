"""Release-blocking conformance tests for the modular ATLAS governance skill family."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "plugin-release-policy.yaml"
PLUGIN = ROOT / "plugin.json"
ROOT_SKILL = ROOT / "skills" / "atlas-os" / "SKILL.md"
ARGUS_MODULAR_COMMIT = "0a78e94b1dd2d6d2783a1d1145a70217b022b79b"

SKILLS = {
    "atlas-os": ["Mission Control", "Route"],
    "atlas-action-governance": ["spec/approvals.yaml", "spec/routing.yaml"],
    "atlas-provider-handoff": ["integrations/argus.yaml", "contracts/atlas-argus-execution-v2.json"],
    "atlas-persistence": ["spec/persistence.yaml", "integrations/access-asia.yaml"],
    "atlas-verification": ["spec/verification.yaml", "provider success"],
}


class ModularAtlasSkillFamilyTests(unittest.TestCase):
    def test_all_five_governance_skills_exist_and_preserve_authority(self) -> None:
        for name, required_refs in SKILLS.items():
            path = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {name}\n"), name)
            for ref in required_refs:
                self.assertIn(ref, text, f"{name}: {ref}")
            if name != "atlas-os":
                self.assertIn("does not create new authority", text, name)
                self.assertIn("ATLAS", text, name)

    def test_root_remains_mission_control_router_not_specialist_control_plane(self) -> None:
        text = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("every user prompt enters Mission Control first", text)
        self.assertIn("atlas-action-governance", text)
        self.assertIn("atlas-provider-handoff", text)
        self.assertIn("atlas-persistence", text)
        self.assertIn("atlas-verification", text)
        self.assertIn("exactly", text)
        self.assertIn("Understand + Normalize -> Minimal Domain Framing -> Route", text)

    def test_plugin_package_bundles_and_hashes_every_governance_skill(self) -> None:
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        expected_paths = {f"skills/{name}/SKILL.md" for name in SKILLS}
        self.assertTrue(expected_paths.issubset(set(policy["bundle"]["paths"])))
        self.assertTrue(expected_paths.issubset(set(policy["synchronization"]["wrapper_paths"])))
        self.assertTrue(expected_paths.issubset(set(policy["impact"]["release_required"]["exact"])))
        self.assertIn("spec/persistence.yaml", policy["bundle"]["paths"])
        self.assertIn("integrations/access-asia.yaml", policy["bundle"]["paths"])

    def test_argus_pin_and_plugin_version_match_modular_release(self) -> None:
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertEqual(ARGUS_MODULAR_COMMIT, policy["argus_compatibility"]["compatible_commit"])
        self.assertEqual("3.0.4", plugin["version"])
        self.assertIn("version: 3.0.2", root_skill)


if __name__ == "__main__":
    unittest.main()
