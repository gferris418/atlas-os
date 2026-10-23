import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / ".github" / "plugin-release-policy.yaml"
TOOL = ROOT / "tools" / "plugin_release_gate.py"
ARGUS_VERIFIER = ROOT / "tools" / "verify_argus_compatibility.py"
WORKFLOW = ROOT / ".github" / "workflows" / "plugin-release-gate.yml"
CURRENT_ARGUS_COMMIT = "0454024624eafe704d740ca2fc6fd1cc3dba0bfd"
CURRENT_ARGUS_CONTRACT_VERSION = "1.0.1"


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

    def test_policy_tracks_current_argus_compatibility_contract(self):
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        argus = policy["argus_compatibility"]
        self.assertEqual(CURRENT_ARGUS_COMMIT, argus["compatible_commit"])
        self.assertEqual(CURRENT_ARGUS_CONTRACT_VERSION, argus["contract_version"])

    def test_classifier_requires_release_for_chatgpt_and_argus_boundary_changes(self):
        self.assertTrue(TOOL.is_file(), "missing plugin release classifier")
        module = load_gate_module()
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        self.assertTrue(module.classify_paths(["skills/atlas-os/SKILL.md"], policy)["release_required"])
        self.assertTrue(module.classify_paths(["integrations/argus.yaml"], policy)["release_required"])
        self.assertFalse(module.classify_paths(["docs/examples.md"], policy)["release_required"])

    def test_release_control_changes_require_review_without_forcing_plugin_release(self):
        module = load_gate_module()
        policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))

        result = module.classify_paths(
            [
                ".github/plugin-release-policy.yaml",
                ".github/workflows/plugin-release-gate.yml",
            ],
            policy,
        )

        self.assertFalse(result["release_required"])
        self.assertTrue(result["review_required"])
        self.assertEqual(
            [
                ".github/plugin-release-policy.yaml",
                ".github/workflows/plugin-release-gate.yml",
            ],
            result["review_matches"],
        )

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

    def test_workflow_checks_out_and_verifies_the_pinned_argus_revision(self):
        self.assertTrue(ARGUS_VERIFIER.is_file(), "missing ARGUS compatibility verifier")
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: Read ARGUS compatibility pin", text)
        self.assertIn("name: Checkout compatible ARGUS", text)
        self.assertIn("python tools/verify_argus_compatibility.py", text)

        workflow = yaml.safe_load(text)
        self.assertIn("argus-compatibility", workflow["jobs"])
        compatibility_steps = workflow["jobs"]["argus-compatibility"]["steps"]
        release_steps = workflow["jobs"]["plugin-release-gate"]["steps"]
        self.assertIn("Checkout compatible ARGUS", [step.get("name") for step in compatibility_steps])
        self.assertNotIn("Checkout compatible ARGUS", [step.get("name") for step in release_steps])
        self.assertFalse(
            any(step.get("with", {}).get("cache") for step in compatibility_steps),
            "untrusted compatibility checkout must not share a dependency cache",
        )


if __name__ == "__main__":
    unittest.main()
