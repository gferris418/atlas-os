from __future__ import annotations

import unittest
from inspect import signature

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

    def test_specialist_and_research_routing_is_previewed_before_execution(self) -> None:
        result = execute(ExecutionEnvelope(
            objective=(
                "Find and assess public procurement opportunities for coastal "
                "surveillance radar for Bangladesh Navy using public sources only"
            ),
            task_id="TASK-BD-RADAR-OPPORTUNITIES",
            plan_id="plan-bd-radar-opportunities",
            work_units=(
                {"id": "research", "status": "PENDING", "dependencies": []},
            ),
            surface="chatgpt",
            clarification_status="RESOLVED",
            timestamp="2026-10-21T22:45:00+06:00",
            timezone_name="Asia/Dhaka",
        ))

        self.assertEqual("BLOCKED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])
        self.assertEqual("PROPOSED", result.routing_preview["status"])
        self.assertIn("task_id", result.routing_preview)
        self.assertEqual("TASK-BD-RADAR-OPPORTUNITIES", result.routing_preview["task_id"])
        self.assertEqual("plan-bd-radar-opportunities", result.routing_preview["plan_id"])
        self.assertEqual("chatgpt", result.routing_preview["surface"])
        self.assertIn("work_unit", result.routing_preview)
        self.assertEqual("research", result.routing_preview["work_unit"])
        self.assertEqual(
            [
                "government_public_sector_opportunity_intelligence",
                "public_research",
            ],
            result.routing_preview["requirements"],
        )
        self.assertEqual(
            {
                "domain-method.argus-intelligence",
                "skill.evidence-research",
                "tool.public-research",
            },
            {provider["id"] for provider in result.routing_preview["providers"]},
        )
        for provider in result.routing_preview["providers"]:
            with self.subTest(provider=provider["id"]):
                self.assertTrue(provider["purpose"])
                self.assertTrue(provider["method"])
                self.assertIn(provider["permission"], {"read", "write"})
                self.assertIn("fallback", provider)
        self.assertTrue(result.routing_preview["digest"].startswith("sha256:"))
        self.assertEqual("ROUTING_PREVIEW", result.execution_trace[-1])
        self.assertNotIn("EXECUTION", result.execution_trace)

    def test_execution_envelope_exposes_bound_routing_approval_fields(self) -> None:
        parameters = signature(ExecutionEnvelope).parameters
        self.assertIn("task_id", parameters)
        self.assertIn("routing_approval_status", parameters)
        self.assertIn("routing_preview_digest", parameters)

    def test_exact_preview_approval_routes_research_providers_before_execution(self) -> None:
        request = {
            "objective": "Find current public sources about ISO 9001",
            "task_id": "TASK-ISO-9001-RESEARCH",
            "plan_id": "plan-iso-9001-research",
            "work_units": (
                {"id": "research", "status": "PENDING", "dependencies": []},
            ),
            "surface": "chatgpt",
        }
        proposal = execute(ExecutionEnvelope(**request))

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("READY", approved.state)
        self.assertEqual("research", approved.active_unit)
        self.assertEqual(
            {"skill.evidence-research", "tool.public-research"},
            {decision["provider_id"] for decision in approved.routing_decisions},
        )
        self.assertTrue(all(
            decision["status"] == "ROUTED"
            for decision in approved.routing_decisions
        ))
        self.assertLess(
            approved.execution_trace.index("ROUTING"),
            approved.execution_trace.index("EXECUTION"),
        )

    def test_rejected_or_stale_routing_preview_cannot_execute(self) -> None:
        request = {
            "objective": "Find current public sources about ISO 9001",
            "task_id": "TASK-ISO-9001-RESEARCH",
            "plan_id": "plan-iso-9001-research",
            "work_units": (
                {"id": "research", "status": "PENDING", "dependencies": []},
            ),
            "surface": "chatgpt",
        }
        proposal = execute(ExecutionEnvelope(**request))
        cases = (
            ("REJECTED", proposal.routing_preview["digest"], "rejected"),
            ("APPROVED", "sha256:" + "0" * 64, "does not match"),
        )

        for status, digest, expected_blocker in cases:
            with self.subTest(status=status):
                result = execute(ExecutionEnvelope(
                    **request,
                    routing_approval_status=status,
                    routing_preview_digest=digest,
                ))
                self.assertEqual("BLOCKED", result.state)
                self.assertIsNone(result.active_unit)
                self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])
                self.assertIn(expected_blocker, result.dashboard["blocker_or_approval"])
                self.assertEqual((), result.routing_decisions)
                self.assertNotIn("EXECUTION", result.execution_trace)

    def test_approved_argus_preview_still_requires_acceptable_domain_handoff(self) -> None:
        request = {
            "objective": (
                "Find and assess public procurement opportunities for coastal "
                "surveillance radar for Bangladesh Navy using public sources only"
            ),
            "task_id": "TASK-BD-RADAR-OPPORTUNITIES",
            "plan_id": "plan-bd-radar-opportunities",
            "work_units": (
                {"id": "research", "status": "PENDING", "dependencies": []},
            ),
            "surface": "chatgpt",
            "clarification_status": "RESOLVED",
            "timestamp": "2026-10-21T22:45:00+06:00",
            "timezone_name": "Asia/Dhaka",
        }
        proposal = execute(ExecutionEnvelope(**request))

        result = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        argus = next(
            decision
            for decision in result.routing_decisions
            if decision["provider_id"] == "domain-method.argus-intelligence"
        )
        self.assertEqual("BLOCKED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertEqual("ROUTING", result.dashboard["active_stage"])
        self.assertEqual("BLOCKED", argus["status"])
        self.assertEqual("HANDOFF_STATE_NOT_ACCEPTED", argus["reason"])
        self.assertTrue(argus["handoff_id"].startswith("HANDOFF-"))
        self.assertNotIn("EXECUTION", result.execution_trace)

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
