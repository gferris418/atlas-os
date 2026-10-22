from __future__ import annotations

import unittest

from atlas_runtime import ARGUS_APPROVAL, ExecutionEnvelope, PRE_EXECUTION_FLOW, execute


class RuntimeTests(unittest.TestCase):
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

    def test_provider_return_always_returns_to_atlas(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Assess ST Engineering opportunity evidence.",
            task_id="TASK-2",
            approvals=(ARGUS_APPROVAL,),
            provider_result={"provider": "argus", "status": "complete"},
        ))
        self.assertEqual("ATLAS", result.provider_return_target)
        self.assertEqual("ATLAS", result.next_step_authority)
        self.assertIn("PROVIDER_RETURN_RECONCILIATION", result.execution_trace)
        self.assertIn("REROUTE", result.dashboard["next_action"])

    def test_generated_task_id_is_deterministic(self) -> None:
        first = execute(ExecutionEnvelope(objective="Explain procurement policy."))
        second = execute(ExecutionEnvelope(objective="Explain   procurement policy."))
        self.assertEqual(first.task_id, second.task_id)


if __name__ == "__main__":
    unittest.main()
