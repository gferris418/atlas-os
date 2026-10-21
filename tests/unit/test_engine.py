from __future__ import annotations

import unittest

from atlas_runtime import ExecutionEnvelope, execute


class ExecutionEngineTests(unittest.TestCase):
    def test_execute_compiles_one_governed_execution_result(self) -> None:
        envelope = ExecutionEnvelope(
            objective="  Assess   coastal surveillance radar  ",
            plan_id="plan-radar",
            work_units=(
                {
                    "id": "classify",
                    "status": "COMPLETED",
                    "dependencies": [],
                },
                {
                    "id": "assess",
                    "status": "PENDING",
                    "dependencies": ["classify"],
                },
            ),
            surface="chatgpt",
            timestamp="2026-10-19T01:00:00+06:00",
            timezone_name="Asia/Dhaka",
        )

        result = execute(envelope)

        self.assertEqual("BLOCKED", result.state)
        self.assertEqual("Assess coastal surveillance radar", result.normalized_intent)
        self.assertEqual(("classify", "assess"), result.plan)
        self.assertIsNone(result.active_unit)
        self.assertIn("ANALYSIS", result.task_classes)
        self.assertEqual("ROUTED", result.taxonomy_route["status"])
        self.assertEqual("maritime-defense", result.taxonomy_route["hierarchy"]["vertical"])
        self.assertEqual("PARTIAL", result.domain_classification["status"])
        self.assertEqual("PASS", result.capability_audit["status"])
        self.assertEqual("TAXONOMY_ROUTING", result.execution_trace[0])
        self.assertIn("CAPABILITY_AUDIT", result.execution_trace)
        self.assertNotIn("EXECUTION", result.execution_trace)
        self.assertEqual("chatgpt", result.dashboard["surface"])
        self.assertEqual("BLOCKED", result.dashboard["plan_status"])
        self.assertEqual("MATERIAL_CONTEXT_MATRIX", result.dashboard["active_stage"])
        self.assertEqual("PENDING", result.dashboard["clarification_status"])
        self.assertEqual("BLOCKED", result.dashboard["quality_gate"])
        self.assertIn("how", result.dashboard["blocker_or_approval"])
        self.assertEqual(50, result.dashboard["progress"])
        self.assertLessEqual(len(result.compact_status.splitlines()), 4)
        for label in ("Input", "Processing", "Output", "Playbook", "Framework", "SOP"):
            with self.subTest(label=label):
                self.assertIn(label, result.compact_status)
        self.assertIn("Taxonomy ROUTED", result.dashboard["processing_summary"])

    def test_explicitly_resolved_clarification_unlocks_routed_execution(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Assess coastal surveillance radar",
            plan_id="plan-radar-resolved",
            work_units=(
                {"id": "assess", "status": "PENDING", "dependencies": []},
            ),
            clarification_status="RESOLVED",
        ))

        self.assertEqual("READY", result.state)
        self.assertEqual("assess", result.active_unit)
        self.assertEqual("READY", result.dashboard["plan_status"])
        self.assertEqual("RESOLVED", result.dashboard["clarification_status"])
        self.assertEqual("EXECUTION", result.execution_trace[-1])

    def test_execute_consumes_work_units_once_and_does_not_mutate_them(self) -> None:
        source = [
            {"id": "answer", "status": "PENDING", "dependencies": []},
        ]
        envelope = ExecutionEnvelope(
            objective="Answer the question",
            plan_id="plan-answer",
            work_units=(item for item in source),
        )

        result = execute(envelope)

        source[0]["status"] = "FAILED"
        self.assertEqual(("answer",), result.plan)
        self.assertEqual("answer", result.active_unit)
        self.assertEqual("READY", result.state)

    def test_execute_rejects_an_empty_execution_envelope(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one work unit"):
            ExecutionEnvelope(
                objective="Answer",
                plan_id="plan-answer",
                work_units=(),
            )

    def test_execution_accepts_any_valid_ai_host_identifier(self) -> None:
        for surface in ("hermes-agent", "custom-ai-tool"):
            with self.subTest(surface=surface):
                envelope = ExecutionEnvelope(
                    objective="Answer with ATLAS governance",
                    plan_id=f"plan-{surface}",
                    work_units=(
                        {"id": "answer", "status": "PENDING", "dependencies": []},
                    ),
                    surface=surface,
                )
                self.assertEqual(surface, execute(envelope).dashboard["surface"])

    def test_execution_rejects_invalid_ai_host_identifiers(self) -> None:
        for surface in ("Windows 11", "../agent", "", "A" * 65):
            with self.subTest(surface=surface), self.assertRaisesRegex(
                ValueError, "surface identifier"
            ):
                ExecutionEnvelope(
                    objective="Answer",
                    plan_id="plan-answer",
                    work_units=(
                        {"id": "answer", "status": "PENDING", "dependencies": []},
                    ),
                    surface=surface,
                )


if __name__ == "__main__":
    unittest.main()
