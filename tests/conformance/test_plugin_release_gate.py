import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "plugin-release-policy.yaml"
TOOL = ROOT / "tools" / "plugin_release_gate.py"
WORKFLOW = ROOT / ".github" / "workflows" / "plugin-release-gate.yml"
CURRENT_ARGUS_COMMIT = "250dc38f0415a71d72536beff3c8426878b10fa3"
CURRENT_ARGUS_CONTRACT_VERSION = "2.0.0"


def load_gate_module():
    spec = importlib.util.spec_from_file_location("plugin_release_gate", TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PluginReleaseGateContract(unittest.TestCase):
    def test_policy_declares_guarded_manual_publication_and_bundle(self):
        self.assertTrue(POLICY.is_file(), "missing plugin release policy")
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        self.assertEqual("1.1.0", policy["version"])
        self.assertEqual("atlas-os", policy["plugin"]["name"])
        self.assertEqual("gferris418/atlas-os", policy["plugin"]["canonical_repository"])
        self.assertFalse(policy["publication"]["automatic"])
        self.assertEqual("plugin_creator_guarded_update", policy["publication"]["mechanism"])
        self.assertTrue(policy["publication"]["preserve_plugin_identity"])
        self.assertIn("plugin.json", policy["bundle"]["paths"])
        self.assertIn("skills/atlas-os/SKILL.md", policy["bundle"]["paths"])
        self.assertIn("integrations/chatgpt-bootstrap.yaml", policy["bundle"]["paths"])
        self.assertIn("integrations/argus.yaml", policy["bundle"]["paths"])
        self.assertIn("spec/persistence.yaml", policy["bundle"]["paths"])
        self.assertIn("integrations/access-asia.yaml", policy["bundle"]["paths"])

        sync = policy["synchronization"]
        self.assertEqual("chatgpt_plugin_sync_required", sync["event_type"])
        self.assertEqual("plugin-sync-request.json", sync["request_file"])
        self.assertEqual("sha256", sync["hash_algorithm"])
        self.assertEqual(["plugin.json", "skills/atlas-os/SKILL.md"], sync["wrapper_paths"])
        self.assertTrue(sync["artifact_only_publication_input"])
        self.assertTrue(sync["publication_receipt_required"])

    def test_policy_tracks_current_argus_compatibility_contract(self):
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        argus = policy["argus_compatibility"]
        self.assertEqual(CURRENT_ARGUS_COMMIT, argus["compatible_commit"])
        self.assertEqual(CURRENT_ARGUS_CONTRACT_VERSION, argus["contract_version"])

    def test_classifier_requires_release_for_chatgpt_argus_and_persistence_boundary_changes(self):
        self.assertTrue(TOOL.is_file(), "missing plugin release classifier")
        module = load_gate_module()
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        self.assertTrue(module.classify_paths(["skills/atlas-os/SKILL.md"], policy)["release_required"])
        self.assertTrue(module.classify_paths(["integrations/argus.yaml"], policy)["release_required"])
        self.assertTrue(module.classify_paths(["spec/persistence.yaml"], policy)["release_required"])
        self.assertTrue(module.classify_paths(["integrations/access-asia.yaml"], policy)["release_required"])
        self.assertFalse(module.classify_paths(["docs/examples.md"], policy)["release_required"])

    def test_metadata_is_traceable_to_atlas_and_argus_commits(self):
        self.assertTrue(TOOL.is_file(), "missing plugin release classifier")
        module = load_gate_module()
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

    def test_missing_changed_path_file_fails_closed(self):
        module = load_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.txt"
            with self.assertRaises(FileNotFoundError):
                module._read_changed_paths(missing)

    def test_workflow_builds_exact_recorded_revision_after_validation(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}", text)
        self.assertIn("name: Validate release revision", text)
        self.assertIn("python -m unittest discover -s tests/unit -v", text)
        self.assertIn("python -m unittest discover -s tests/conformance -v", text)
        self.assertIn("python -m unittest discover -s tests/integration -v", text)
        self.assertIn("python tools/validate.py .", text)
        self.assertLess(text.index("name: Validate release revision"), text.index("name: Classify plugin impact and prepare release bundle"))

    def test_workflow_emits_hashed_event_driven_sync_handoff(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Build synchronization request", text)
        self.assertIn("hashlib.sha256", text)
        self.assertIn("plugin-sync-request.json", text)
        self.assertIn("chatgpt_plugin_sync_required", text)
        self.assertIn("name: Emit repository synchronization event", text)
        self.assertIn("needs.plugin-release-gate.outputs.release_required == 'true'", text)


if __name__ == "__main__":
    unittest.main()
