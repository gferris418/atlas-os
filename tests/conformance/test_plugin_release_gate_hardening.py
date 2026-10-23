from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.plugin_release_gate import classify_paths, load_policy, validate_argus_checkout

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "plugin-release-policy.yaml"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "plugin-release-gate.yml"


class PluginReleaseGateHardeningTests(unittest.TestCase):
    def test_policy_and_gate_workflow_changes_require_review(self) -> None:
        policy = load_policy(POLICY_PATH)
        for path in (
            ".github/plugin-release-policy.yaml",
            ".github/workflows/plugin-release-gate.yml",
        ):
            result = classify_paths([path], policy)
            self.assertFalse(result["release_required"])
            self.assertTrue(result["review_required"])
            self.assertEqual([path], result["review_matches"])

    def test_workflow_checks_out_and_validates_pinned_argus_contract(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("Checkout pinned ARGUS contract", workflow)
        self.assertIn("repository: gferris418/argus-intelligence", workflow)
        self.assertIn("ref: ${{ steps.argus_pin.outputs.commit }}", workflow)
        self.assertIn("--argus-root .argus-contract", workflow)

    def test_argus_checkout_validation_binds_git_head_contract_and_atlas_release(self) -> None:
        base_policy = load_policy(POLICY_PATH)
        atlas_version = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))["version"]

        with tempfile.TemporaryDirectory() as tmp:
            argus_root = Path(tmp)
            contract_dir = argus_root / "contracts" / "atlas"
            contract_dir.mkdir(parents=True)
            descriptor = {
                "version": base_policy["argus_compatibility"]["contract_version"],
                "status": "CURRENT",
                "atlas": {
                    "repository": base_policy["plugin"]["canonical_repository"],
                    "version": atlas_version,
                    "commit": "release-commit-is-validated-by-ARGUS-contract-tests",
                },
                "contract": {
                    "prompt_entry": "MISSION_CONTROL_FIRST",
                    "prompt_entry_scope": "every_user_prompt_while_atlas_active",
                    "capability": "intelligence_collection",
                    "provider": "argus",
                    "approval_key": "ARGUS_ACTIVATION",
                    "activation_authority": "ATLAS",
                    "next_step_authority": "ATLAS",
                    "provider_return_target": "ATLAS",
                    "explicit_user_approval_required": True,
                    "pre_execution_flow": [
                        "UNDERSTAND_AND_NORMALIZE",
                        "MINIMAL_DOMAIN_FRAMING",
                        "ROUTE",
                    ],
                    "plugin_release_impact": "contracts/atlas/plugin-release-impact.yaml",
                },
            }
            (contract_dir / "current-integration.yaml").write_text(
                yaml.safe_dump(descriptor, sort_keys=False), encoding="utf-8"
            )
            (contract_dir / "plugin-release-impact.yaml").write_text(
                yaml.safe_dump(
                    {
                        "version": "1.0.0",
                        "status": "CURRENT",
                        "boundary_changes": {
                            "plugin_review_required": True,
                            "atlas_release_decision_required": True,
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            subprocess.run(["git", "init", "-q"], cwd=argus_root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=argus_root, check=True)
            subprocess.run(["git", "config", "user.name", "ATLAS Test"], cwd=argus_root, check=True)
            subprocess.run(["git", "add", "."], cwd=argus_root, check=True)
            subprocess.run(["git", "commit", "-qm", "fixture"], cwd=argus_root, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=argus_root, text=True).strip()

            policy = copy.deepcopy(base_policy)
            policy["argus_compatibility"]["compatible_commit"] = head
            validated = validate_argus_checkout(argus_root, policy, atlas_root=ROOT)
            self.assertEqual(head, validated["commit"])
            self.assertEqual(
                base_policy["argus_compatibility"]["contract_version"],
                validated["contract_version"],
            )
            self.assertEqual(atlas_version, validated["atlas_version"])

            wrong_policy = copy.deepcopy(policy)
            wrong_policy["argus_compatibility"]["compatible_commit"] = "0" * 40
            with self.assertRaises(ValueError):
                validate_argus_checkout(argus_root, wrong_policy, atlas_root=ROOT)


if __name__ == "__main__":
    unittest.main()
