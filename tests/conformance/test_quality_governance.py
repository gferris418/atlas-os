from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "spec/quality-governance.yaml"
MANIFEST = ROOT / "atlas-os.yaml"
CORE = ROOT / "spec/core.yaml"


class QualityGovernanceConformanceTests(unittest.TestCase):
    def test_quality_governance_is_normative_and_registered(self) -> None:
        self.assertTrue(QUALITY.is_file())
        quality = yaml.safe_load(QUALITY.read_text(encoding="utf-8"))
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(quality["normative"])
        self.assertIn("spec/quality-governance.yaml", manifest["specifications"])

    def test_quality_hierarchy_places_performance_after_intelligence_quality(self) -> None:
        quality = yaml.safe_load(QUALITY.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(
            [
                "QUALITY_DECISION_UTILITY",
                "EVIDENCE_VERIFIABILITY",
                "COMPLETENESS",
                "ACCURACY_CONSISTENCY",
                "PERFORMANCE",
                "COST_TOKEN_EFFICIENCY",
            ],
            quality["optimization_hierarchy"],
        )
        self.assertTrue(quality["performance_invariant"]["may_not_lower_required_quality_tier"])
        self.assertTrue(quality["performance_invariant"]["may_not_bypass_evidence_or_verification"])
        self.assertTrue(quality["performance_invariant"]["may_not_bypass_governance_or_approval"])

    def test_all_q0_q5_tiers_are_defined_and_tier_is_derived_inside_domain_framing(self) -> None:
        quality = yaml.safe_load(QUALITY.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(["Q0", "Q1", "Q2", "Q3", "Q4", "Q5"], list(quality["tiers"]))
        self.assertEqual("MINIMAL_DOMAIN_FRAMING", quality["tier_assignment_stage"])
        self.assertEqual("maximum_assurance_with_explicit_stopping_justification", quality["tiers"]["Q5"]["mode"])

    def test_incremental_reuse_is_quality_gated_and_atlas_owned(self) -> None:
        quality = yaml.safe_load(QUALITY.read_text(encoding="utf-8"))["contract"]
        reuse = quality["incremental_intelligence"]
        self.assertEqual(["REUSE", "REFRESH_DELTA", "RECOLLECT"], reuse["recommendations"])
        self.assertEqual("ATLAS", reuse["decision_authority"])
        self.assertIn("freshness", reuse["reuse_checks"])
        self.assertIn("contradiction_status", reuse["reuse_checks"])
        self.assertIn("invalidation_triggers", reuse["reuse_checks"])
        self.assertIn("required_vs_achieved_quality", reuse["reuse_checks"])

    def test_quality_gate_precedes_authoritative_delivery(self) -> None:
        quality = yaml.safe_load(QUALITY.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(["PASS", "CONTINUE", "IRREDUCIBLE_GAP"], quality["quality_gate"]["outcomes"])
        self.assertTrue(quality["quality_gate"]["required_before_authoritative_delivery"])
        self.assertTrue(quality["quality_gate"]["aggregate_confidence_cannot_override_mandatory_gates"])

    def test_existing_three_step_preprocessing_remains_exact(self) -> None:
        core = yaml.safe_load(CORE.read_text(encoding="utf-8"))
        self.assertEqual(
            ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            core["contract"]["pre_execution_flow"],
        )


if __name__ == "__main__":
    unittest.main()
