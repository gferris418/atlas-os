from __future__ import annotations

import unittest

from atlas_runtime import ExecutionEnvelope, execute
from atlas_runtime.render import progress_for_stage, render_fast_text


class FastTextRendererTests(unittest.TestCase):
    def test_stage_progress_is_deterministic(self) -> None:
        self.assertEqual(5, progress_for_stage("MISSION_CONTROL"))
        self.assertEqual(35, progress_for_stage("ROUTE"))
        self.assertEqual(60, progress_for_stage("EXECUTION"))
        self.assertEqual(80, progress_for_stage("QUALITY_GATE"))
        self.assertEqual(90, progress_for_stage("FINAL_VERIFY"))
        self.assertEqual(95, progress_for_stage("PERSISTENCE"))
        self.assertEqual(100, progress_for_stage("COMPLETE"))

    def test_fast_text_is_compact_plain_text_with_progress_and_control_plane(self) -> None:
        result = execute(ExecutionEnvelope(objective="Explain procurement policy."))
        rendered = render_fast_text(result)
        first, second = rendered.splitlines()
        self.assertTrue(first.startswith("ATLAS ["))
        self.assertIn("% | MC:", first)
        self.assertIn("| CP:", first)
        self.assertIn("| STATUS:", first)
        self.assertIn("| BLOCKER:", first)
        self.assertTrue(second.startswith("NEXT: "))
        self.assertNotIn("| --- |", rendered)

    def test_rendering_does_not_mutate_required_quality_tier(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Should Access Asia pursue this programme and which supplier should we approach?"
        ))
        before = result.domain_framing["required_quality_tier"]
        render_fast_text(result)
        self.assertEqual(before, result.domain_framing["required_quality_tier"])
        self.assertEqual("Q4", before)


if __name__ == "__main__":
    unittest.main()
