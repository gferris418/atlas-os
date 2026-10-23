from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FrameworkDomainBoundaryTests(unittest.TestCase):
    def test_access_asia_business_state_machines_are_not_atlas_runtime_modules(self) -> None:
        forbidden = (
            "atlas_runtime/bid_workflow.py",
            "atlas_runtime/project_handover.py",
            "atlas_runtime/project_execution.py",
            "atlas_runtime/commercial_payment.py",
        )
        for relative_path in forbidden:
            with self.subTest(path=relative_path):
                self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_access_asia_integration_is_deployment_profile_not_core_architecture(self) -> None:
        integration = (ROOT / "integrations/access-asia.yaml").read_text(encoding="utf-8")
        self.assertIn("role: deployment_profile", integration)
        self.assertIn("This profile is not ATLAS core architecture", integration)

    def test_argus_is_described_as_governed_bi_playbook_not_underlying_tool_provider(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("360° Business Intelligence playbook", readme)
        self.assertNotIn("ARGUS is the provider for structured `intelligence_collection`", readme)


if __name__ == "__main__":
    unittest.main()
