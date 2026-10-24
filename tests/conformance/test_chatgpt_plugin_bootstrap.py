import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_MANIFEST = ROOT / "plugin.json"
PACKAGED_SKILL = ROOT / "skills" / "atlas-os" / "SKILL.md"
AGENT_SKILL = ROOT / ".agents" / "skills" / "atlas-os" / "SKILL.md"
CHATGPT_INTEGRATION = ROOT / "integrations" / "chatgpt.yaml"
BOOTSTRAP_CONTRACT = ROOT / "integrations" / "chatgpt-bootstrap.yaml"
MISSION_CONTROL = ROOT / "spec" / "mission-control.yaml"


class ChatGPTPluginBootstrapContract(unittest.TestCase):
    def test_repository_is_a_portable_skills_plugin(self):
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            manifest["$schema"],
        )
        self.assertEqual("atlas-os", manifest["name"])
        self.assertEqual("3.0.4", manifest["version"])
        self.assertIn("execution governance", manifest["description"].lower())
        self.assertIn("mission control", manifest["description"].lower())
        self.assertTrue(PACKAGED_SKILL.is_file())

    def test_packaged_skill_matches_agent_skill_exactly(self):
        self.assertEqual(
            AGENT_SKILL.read_text(encoding="utf-8"),
            PACKAGED_SKILL.read_text(encoding="utf-8"),
        )

    def test_mission_control_is_mandatory_first_prompt_entry_gate(self):
        mission_control = yaml.safe_load(MISSION_CONTROL.read_text(encoding="utf-8"))
        prompt_entry = mission_control["contract"]["prompt_entry"]
        self.assertEqual("EVERY_ATLAS_GOVERNED_PROMPT", prompt_entry["scope"])
        self.assertEqual("FIRST", prompt_entry["order"])
        self.assertTrue(prompt_entry["before_pre_execution_flow"])
        self.assertTrue(prompt_entry["no_tool_or_provider_before_entry"])

        bootstrap = yaml.safe_load(BOOTSTRAP_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual("MISSION_CONTROL_FIRST", bootstrap["bootstrap"]["prompt_entry"])
        self.assertEqual(
            "every_user_prompt_while_atlas_active",
            bootstrap["bootstrap"]["prompt_entry_scope"],
        )
        self.assertTrue(bootstrap["guarantees"]["mission_control_first_when_atlas_active"])
        self.assertFalse(bootstrap["guarantees"]["universal_prompt_injection"])

        skill = PACKAGED_SKILL.read_text(encoding="utf-8").lower()
        self.assertIn("every user prompt", skill)
        self.assertIn("mission control", skill)
        self.assertIn("before the three-step pre-execution flow", skill)

    def test_bootstrap_contract_uses_live_github_as_canonical_source(self):
        bootstrap = yaml.safe_load(BOOTSTRAP_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual("1.0.1", bootstrap["version"])
        self.assertEqual("gferris418/atlas-os", bootstrap["canonical_repository"])
        self.assertEqual("main", bootstrap["canonical_ref"])
        self.assertEqual("github_live_when_available", bootstrap["source_resolution"])
        self.assertEqual("/AI Frameworks/ATLAS-ARGUS", bootstrap["library_bootstrap"]["root"])
        self.assertEqual("cache_bootstrap_not_canonical", bootstrap["library_bootstrap"]["role"])
        self.assertEqual("gferris418/argus-intelligence", bootstrap["argus"]["repository"])
        self.assertTrue(bootstrap["argus"]["explicit_user_approval_required"])
        self.assertEqual("ATLAS", bootstrap["argus"]["next_step_authority"])
        self.assertEqual("relevance_triggered_plugin_skill", bootstrap["surfaces"]["chat"])
        self.assertEqual("relevance_triggered_plugin_skill", bootstrap["surfaces"]["work"])
        self.assertEqual("relevance_triggered_plugin_skill", bootstrap["surfaces"]["projects"])
        self.assertFalse(bootstrap["guarantees"]["universal_prompt_injection"])

    def test_chatgpt_host_adapter_references_bootstrap_contract(self):
        integration = yaml.safe_load(CHATGPT_INTEGRATION.read_text(encoding="utf-8"))
        self.assertEqual("3.0.2", integration["version"])
        self.assertEqual("plugin.json", integration["plugin_manifest"])
        self.assertEqual("integrations/chatgpt-bootstrap.yaml", integration["bootstrap_contract"])
        self.assertEqual("skills/atlas-os/SKILL.md", integration["primary_skill"])


if __name__ == "__main__":
    unittest.main()
