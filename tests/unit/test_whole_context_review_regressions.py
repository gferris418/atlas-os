from __future__ import annotations

import unittest

from atlas_runtime import (
    ExecutionContext,
    ExecutionEnvelope,
    execute,
    prepare_domain_context_handoff,
)


class WholeContextReviewRegressionTests(unittest.TestCase):
    def test_legacy_task_without_semantic_context_does_not_assume_clarity(self) -> None:
        task = {
            "id": "TASK-LEGACY-AMBIGUOUS",
            "inputs": [{"type": "user_prompt", "value": "radar for bank"}],
            "domain_classification": {
                "status": "RESEARCH_REQUIRED",
                "facets": {},
                "taxonomy_references": [],
                "risk_flags": [],
                "unresolved_facets": ["domain"],
                "conditional_candidates": [],
                "evidence": [],
                "next_action": "Resolve intended meaning.",
            },
            "domain_alignment": {
                "domains": ["unknown"],
                "status": "RESEARCH_REQUIRED",
                "frameworks": [],
                "applicability": {},
                "deviations": [],
                "compliance": "NOT_CLAIMED",
                "evidence": [],
            },
        }
        handoff = prepare_domain_context_handoff(
            task,
            execution_context=ExecutionContext(
                task_id="TASK-LEGACY-AMBIGUOUS",
                plan_id="plan-legacy-ambiguous",
                work_unit_id="unit-collection",
                task_class="RESEARCH",
            ),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-LEGACY-AMBIGUOUS",
            created_at="2026-10-22T16:40:00+06:00",
        )
        self.assertEqual("AMBIGUOUS", handoff["semantic_context"]["status"])
        self.assertEqual("BLOCKED", handoff["state"])
        self.assertTrue(handoff["semantic_context"]["meaning_ambiguities"])

    def test_pending_clarification_returns_governed_block_without_provider_preview(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Assess coastal surveillance radar",
            plan_id="plan-radar-pending-clarification",
            work_units=(
                {"id": "assess", "status": "PENDING", "dependencies": []},
            ),
            clarification_status="PENDING",
        ))
        self.assertEqual("BLOCKED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertEqual("MATERIAL_CONTEXT_MATRIX", result.dashboard["active_stage"])
        self.assertIn("clarification", result.dashboard["blocker_or_approval"].lower())
        self.assertNotIn("EXECUTION", result.execution_trace)


if __name__ == "__main__":
    unittest.main()
