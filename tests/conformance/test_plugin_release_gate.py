import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "plugin-release-policy.yaml"
TOOL = ROOT / "tools" / "plugin_release_gate.py"


class PluginReleaseGateContract(unittest.TestCase):
    def test_policy_declares_guarded_manual_publication_and_bundle(self):
        self.assertTrue(POLICY.is_file(), "missing plugin release policy")
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        self.assertEqual("1.0.0", policy["version"])
        self.assertEqual("atlas-os", policy["plugin"]["name"])
        self.assertEqual("gferris418/atlas-os", policy["plugin"]["canonical_repository"])
        self.assertFalse(policy["publication"]["automatic"])
        self.assertEqual("plugin_creator_guarded_update", policy["publication"]["mechanism"])
        self.assertTrue(policy["publication"]["preserve_plugin_identity"])
        self.assertIn("plugin.json", policy["bundle"]["paths"])
        self.assertIn("skills/atlas-os/SKILL.md", policy["bundle"]["paths"])
        self.assertIn("integrations/chatgpt-bootstrap.yaml", policy["bundle"]["paths"])
        self.assertIn("integrations/argus.yaml", policy["bundle"]["paths"])

    def test_classifier_requires_release_for_chatgpt_and_argus_boundary_changes(self):
        self.assertTrue(TOOL.is_file(), "missing plugin release classifier")
        spec = importlib.util.spec_from_file_location("plugin_release_gate", TOOL)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        self.assertTrue(module.classify_paths(["skills/atlas-os/SKILL.md"], policy)["release_required"])
        self.assertTrue(module.classify_paths(["integrations/argus.yaml"], policy)["release_required"])
        self.assertFalse(module.classify_paths(["docs/examples.md"], policy)["release_required"])

    def test_metadata_is_traceable_to_atlas_and_argus_commits(self):
        self.assertTrue(TOOL.is_file(), "missing plugin release classifier")
        spec = importlib.util.spec_from_file_location("plugin_release_gate", TOOL)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        metadata = module.build_metadata(
            policy=policy,
            changed_paths=["plugin.json"],
            atlas_commit="a" * 40,
            argus_commit="b" * 40,
            argus_contract_version="1.0.0",
        )
        self.assertTrue(metadata["release_required"])
        self.assertEqual("a" * 40, metadata["source"]["atlas_commit"])
        self.assertEqual("b" * 40, metadata["source"]["argus_compatible_commit"])
        self.assertEqual("1.0.0", metadata["source"]["argus_contract_version"])
        self.assertEqual("atlas-os", metadata["plugin"]["name"])

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "metadata.json"
            output.write_text(json.dumps(metadata), encoding="utf-8")
            loaded = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(metadata, loaded)


if __name__ == "__main__":
    unittest.main()
