from __future__ import annotations

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class CleanArchitectureContractTests(unittest.TestCase):
    def test_active_spec_surface_is_small_and_canonical(self) -> None:
        expected = {
            "approvals.yaml",
            "canonical-execution-graph.yaml",
            "context.yaml",
            "control-plane.yaml",
            "core.yaml",
            "evidence.yaml",
            "execution.yaml",
            "mission-control.yaml",
            "observability.yaml",
            "persistence.yaml",
            "routing.yaml",
            "verification.yaml",
        }
        actual = {path.name for path in (ROOT / "spec").glob("*.yaml")}
        self.assertEqual(expected, actual)

    def test_historical_and_generated_material_is_not_active_repository_content(self) -> None:
        for relative in ("legacy", "migration", "library", "docs/releases", "docs/plans"):
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_pre_execution_flow_has_exactly_three_steps(self) -> None:
        core = yaml.safe_load((ROOT / "spec/core.yaml").read_text(encoding="utf-8"))
        self.assertEqual(
            ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            core["contract"]["pre_execution_flow"],
        )

    def test_atlas_owns_every_next_step_after_provider_return(self) -> None:
        routing = yaml.safe_load((ROOT / "spec/routing.yaml").read_text(encoding="utf-8"))
        contract = routing["contract"]
        self.assertTrue(contract["atlas_owns_next_step"])
        self.assertEqual("ATLAS", contract["provider_return_target"])
        self.assertEqual(
            {
                "NO_TOOL",
                "DIRECT_SEARCH",
                "DEEP_RESEARCH",
                "ARGUS",
                "SPECIALIST",
                "CONNECTED_SOURCE",
                "CODE_EXECUTION",
                "EXTERNAL_ACTION",
                "MULTI_CAPABILITY",
            },
            set(contract["mechanisms"]),
        )

    def test_argus_is_a_bounded_provider_not_a_peer_os(self) -> None:
        argus = yaml.safe_load((ROOT / "integrations/argus.yaml").read_text(encoding="utf-8"))
        self.assertEqual("intelligence_collection", argus["capability"])
        self.assertEqual("ATLAS", argus["activation_authority"])
        self.assertEqual("ATLAS", argus["next_step_authority"])
        self.assertTrue(argus["explicit_user_approval_required"])

    def test_machine_discovery_contains_no_migration_or_release_history_authority(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        machine_contracts = manifest["machine_contracts"]
        self.assertFalse(any(path.startswith("migration/") for path in machine_contracts))
        self.assertFalse(any(path.startswith("legacy/") for path in machine_contracts))
        self.assertFalse(any("release-verification" in path for path in machine_contracts))

    def test_docs_surface_is_deliberately_small(self) -> None:
        allowed = {
            "README.md", "SUMMARY.md", "architecture.md", "framework.md", "playbook.md", "sop.md",
            "capabilities-routing.md", "evidence-verification.md", "argus-interface.md", "host-integration.md",
            "implementation-guide.md", "examples.md", "classification-standards.md", "canonical-execution-graph.md",
        }
        self.assertEqual(allowed, {path.name for path in (ROOT / "docs").iterdir() if path.is_file()})

    def test_classification_standards_documentation_is_navigable(self) -> None:
        classification_doc = ROOT / "docs" / "classification-standards.md"
        self.assertTrue(classification_doc.is_file())
        summary = (ROOT / "docs" / "SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("classification-standards.md", summary)


if __name__ == "__main__":
    unittest.main()