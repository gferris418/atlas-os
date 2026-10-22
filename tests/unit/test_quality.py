from __future__ import annotations

import unittest

from atlas_runtime import PRE_EXECUTION_FLOW, ExecutionEnvelope, execute, minimal_domain_framing
from atlas_runtime.quality import QUALITY_TIERS, determine_required_quality_tier


class QualityTierTests(unittest.TestCase):
    def test_quality_tiers_are_ordered_q0_through_q5(self) -> None:
        self.assertEqual(("Q0", "Q1", "Q2", "Q3", "Q4", "Q5"), QUALITY_TIERS)

    def test_deterministic_work_is_q0(self) -> None:
        self.assertEqual("Q0", determine_required_quality_tier("Calculate 2 + 2."))

    def test_verified_lookup_is_q1(self) -> None:
        self.assertEqual("Q1", determine_required_quality_tier("What is the closing date of this tender?"))

    def test_normal_analysis_is_q2(self) -> None:
        self.assertEqual("Q2", determine_required_quality_tier("Explain the procurement policy and its main implications."))

    def test_high_assurance_research_is_q3(self) -> None:
        self.assertEqual(
            "Q3",
            determine_required_quality_tier(
                "Investigate these supplier claims and verify them against authoritative sources."
            ),
        )

    def test_strategic_decision_grade_intelligence_is_q4(self) -> None:
        self.assertEqual(
            "Q4",
            determine_required_quality_tier(
                "Should Access Asia pursue the future offshore patrol vessel programme and which OEM should we approach?"
            ),
        )

    def test_critical_maximum_assurance_work_is_q5(self) -> None:
        self.assertEqual(
            "Q5",
            determine_required_quality_tier(
                "Critical board decision: perform maximum-assurance due diligence before an irreversible high-value commitment."
            ),
        )

    def test_explicit_quality_floor_may_raise_but_never_lower_automatic_tier(self) -> None:
        strategic = "Should Access Asia pursue this programme and which supplier should we approach?"
        self.assertEqual("Q4", determine_required_quality_tier(strategic, requested_floor="Q1"))
        self.assertEqual("Q5", determine_required_quality_tier(strategic, requested_floor="Q5"))

    def test_minimal_domain_framing_carries_quality_without_adding_preprocessing_step(self) -> None:
        framing = minimal_domain_framing(
            "Should Access Asia pursue this programme and which supplier should we approach?"
        )
        self.assertEqual("Q4", framing["required_quality_tier"])
        self.assertIn("quality_requirements", framing)
        self.assertEqual(
            ("UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"),
            PRE_EXECUTION_FLOW,
        )

    def test_execution_context_can_raise_quality_floor_without_changing_flow(self) -> None:
        result = execute(
            ExecutionEnvelope(
                objective="Explain this policy.",
                context={"required_quality_floor": "Q4"},
            )
        )
        self.assertEqual("Q4", result.domain_framing["required_quality_tier"])
        self.assertEqual(PRE_EXECUTION_FLOW, result.pre_execution_flow)
        self.assertEqual("MISSION_CONTROL", result.execution_trace[0])


if __name__ == "__main__":
    unittest.main()
