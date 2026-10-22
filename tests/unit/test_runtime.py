from __future__ import annotations

import unittest
from unittest.mock import patch

import atlas_runtime.runtime as runtime_module
from atlas_runtime import ARGUS_APPROVAL, ExecutionEnvelope, PRE_EXECUTION_FLOW, execute, quality_requirements


class RuntimeTests(unittest.TestCase):
    def test_mission_control_executes_before_normalization(self) -> None:
        order: list[str] = []
        real_normalize = runtime_module.normalize_objective

        def record_mission_control(envelope: ExecutionEnvelope) -> str:
            order.append("MISSION_CONTROL")
            return envelope.objective

        def record_normalize(objective: str) -> str:
            order.append("NORMALIZE")
            return real_normalize(objective)

        with (
            patch.object(runtime_module, "enter_mission_control", side_effect=record_mission_control, create=True),
            patch.object(runtime_module, "normalize_objective", side_effect=record_normalize),
        ):
            execute(ExecutionEnvelope(objective="Rewrite this text."))

        self.assertEqual(["MISSION_CONTROL", "NORMALIZE"], order[:2])

    def test_mission_control_is_first_prompt_entry_stage(self) -> None:
        result = execute(ExecutionEnvelope(objective="Rewrite this text."))
        self.assertEqual("MISSION_CONTROL", result.execution_trace[0])
        self.assertEqual(
            ("MISSION_CONTROL", *PRE_EXECUTION_FLOW),
            result.execution_trace[: 1 + len(PRE_EXECUTION_FLOW)],
        )

    def test_exact_three_step_pre_execution_flow(self) -> None:
        result = execute(ExecutionEnvelope(objective="Rewrite this text."))
        self.assertEqual(PRE_EXECUTION_FLOW, result.pre_execution_flow)
        self.assertEqual(
            ("UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"),
            result.pre_execution_flow,
        )

    def test_argus_route_stops_before_activation_without_approval(self) -> None:
        result = execute(ExecutionEnvelope(objective="ST Engineering", task_id="TASK-1"))
        self.assertEqual("AWAITING_APPROVAL", result.state)
        self.assertEqual("ARGUS", result.route.mechanism)
        self.assertEqual("PENDING", result.route.approval_status)
        self.assertEqual("ATLAS", result.next_step_authority)

    def test_argus_route_is_ready_after_explicit_approval(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="ST Engineering",
            task_id="TASK-1",
            approvals=(ARGUS_APPROVAL,),
        ))
        self.assertEqual("READY", result.state)
        self.assertEqual("APPROVED", result.route.approval_status)

    def test_provider_return_always_returns_to_atlas_and_requires_quality_ledger(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Assess ST Engineering opportunity evidence.",
            task_id="TASK-2",
            approvals=(ARGUS_APPROVAL,),
            provider_result={"provider": "argus", "status": "complete"},
        ))
        self.assertEqual("ATLAS", result.provider_return_target)
        self.assertEqual("ATLAS", result.next_step_authority)
        self.assertIn("PROVIDER_RETURN_RECONCILIATION", result.execution_trace)
        self.assertEqual("QUALITY_GATE_BLOCKED", result.state)
        self.assertEqual("CONTINUE", result.dashboard["quality_gate"])
        self.assertIn("quality ledger", result.dashboard["blocker_or_approval"].lower())

    def test_provider_return_with_insufficient_ledger_continues_collection(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Explain procurement policy.",
            provider_result={
                "provider": "research",
                "status": "complete",
                "quality_ledger": {
                    "achieved_tier": "Q1",
                    "passed_requirements": [],
                    "evidence_confidence": 0.99,
                    "irreducible_gaps": [],
                },
            },
        ))
        self.assertEqual("QUALITY_GATE_BLOCKED", result.state)
        self.assertEqual("CONTINUE", result.dashboard["quality_gate"])
        self.assertIn("targeted collection", result.dashboard["next_action"].lower())

    def test_provider_return_with_sufficient_ledger_advances_to_final_verify(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Explain procurement policy.",
            provider_result={
                "provider": "research",
                "status": "complete",
                "quality_ledger": {
                    "achieved_tier": "Q2",
                    "passed_requirements": list(quality_requirements("Q2")),
                    "evidence_confidence": 0.92,
                    "irreducible_gaps": [],
                },
            },
        ))
        self.assertEqual("READY_FOR_FINAL_VERIFY", result.state)
        self.assertEqual("PASS", result.dashboard["quality_gate"])
        self.assertEqual("FINAL_VERIFY", result.dashboard["active_stage"])

    def test_provider_return_with_irreducible_gap_is_not_silently_passed(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Explain procurement policy.",
            provider_result={
                "provider": "research",
                "status": "complete",
                "quality_ledger": {
                    "achieved_tier": "Q1",
                    "passed_requirements": [],
                    "evidence_confidence": 0.99,
                    "irreducible_gaps": ["official source unavailable"],
                },
            },
        ))
        self.assertEqual("QUALITY_GAP_DISCLOSED", result.state)
        self.assertEqual("IRREDUCIBLE_GAP", result.dashboard["quality_gate"])
        self.assertIn("official source unavailable", result.dashboard["quality_gaps"])

    def test_generated_task_id_is_deterministic(self) -> None:
        first = execute(ExecutionEnvelope(objective="Explain procurement policy."))
        second = execute(ExecutionEnvelope(objective="Explain   procurement policy."))
        self.assertEqual(first.task_id, second.task_id)


if __name__ == "__main__":
    unittest.main()
