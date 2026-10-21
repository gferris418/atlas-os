from __future__ import annotations

import hashlib
import json
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
        self.assertEqual(
            "OPPORTUNITY_IDENTIFICATION",
            result.intent_profile["category"],
        )
        self.assertEqual("DISABLED", result.behavioral_learning_state["mode"])
        self.assertEqual("NOT_AUTHORIZED", result.behavioral_learning_state["persistence"])
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
                self.assertIn("prerequisites", provider)
                self.assertIn("unresolved_gates", provider)
                self.assertIn("fallback", provider)
        argus = next(
            provider
            for provider in result.routing_preview["providers"]
            if provider["id"] == "domain-method.argus-intelligence"
        )
        self.assertEqual(
            ["capability.domain-alignment", "capability.evidence-tracking"],
            argus["prerequisites"],
        )
        self.assertIn("domain_handoff_state:BLOCKED", argus["unresolved_gates"])
        self.assertIn(
            "domain-method.argus-intelligence:domain_handoff_state:BLOCKED",
            result.routing_preview["unresolved_gates"],
        )
        digest_payload = {
            key: value
            for key, value in result.routing_preview.items()
            if key != "digest"
        }
        encoded = json.dumps(
            digest_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            "sha256:" + hashlib.sha256(encoded).hexdigest(),
            result.routing_preview["digest"],
        )
        self.assertTrue(result.routing_preview["digest"].startswith("sha256:"))
        self.assertEqual("ROUTING_PREVIEW", result.execution_trace[-1])
        self.assertNotIn("EXECUTION", result.execution_trace)

    def test_repository_engineering_provider_is_previewed_before_routing(self) -> None:
        request = {
            "objective": "Implement and test a repository change",
            "task_id": "TASK-REPOSITORY-CHANGE",
            "plan_id": "plan-repository-change",
            "work_units": (
                {"id": "implement", "status": "PENDING", "dependencies": []},
            ),
            "surface": "codex",
        }
        result = execute(ExecutionEnvelope(**request))

        self.assertEqual("BLOCKED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])
        self.assertEqual("PROPOSED", result.routing_preview["status"])
        self.assertIn("execute", result.routing_preview["requirements"])
        self.assertEqual(
            {"skill.repository-engineering", "tool.execution"},
            {provider["id"] for provider in result.routing_preview["providers"]},
        )
        self.assertEqual(
            ["tool.execution", "skill.repository-engineering"],
            result.routing_preview["execution_sequence"],
        )
        self.assertEqual((), result.routing_decisions)
        self.assertNotIn("EXECUTION", result.execution_trace)

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=result.routing_preview["digest"],
        ))

        self.assertEqual("READY", approved.state)
        self.assertEqual("implement", approved.active_unit)
        self.assertEqual(
            ["tool.execution", "skill.repository-engineering"],
            [decision["provider_id"] for decision in approved.routing_decisions],
        )
        self.assertTrue(all(
            decision["status"] == "ROUTED"
            for decision in approved.routing_decisions
        ))
        self.assertLess(
            approved.execution_trace.index("ROUTING"),
            approved.execution_trace.index("EXECUTION"),
        )

    def test_domain_method_preview_discloses_missing_handoff_timestamp(self) -> None:
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
        ))

        argus = next(
            provider
            for provider in result.routing_preview["providers"]
            if provider["id"] == "domain-method.argus-intelligence"
        )
        self.assertIn("domain_handoff_timestamp:REQUIRED", argus["unresolved_gates"])

    def test_execution_envelope_exposes_bound_routing_approval_fields(self) -> None:
        parameters = signature(ExecutionEnvelope).parameters
        self.assertIn("task_id", parameters)
        self.assertIn("capability_requirements", parameters)
        self.assertIn("provider_inventory", parameters)
        self.assertIn("routing_approval_status", parameters)
        self.assertIn("routing_preview_digest", parameters)

    def test_host_function_uses_public_preview_approval_and_routing_seam(self) -> None:
        request = {
            "objective": "Calculate the governed route estimate",
            "task_id": "TASK-ROUTE-ESTIMATE",
            "plan_id": "plan-route-estimate",
            "work_units": (
                {"id": "calculate", "status": "PENDING", "dependencies": []},
            ),
            "surface": "custom-ai-tool",
            "capability_requirements": ("calculate_route_estimate",),
            "provider_inventory": {
                "function": ({
                    "id": "function.route-estimator",
                    "name": "Route estimator",
                    "description": "Calculates a route estimate from approved inputs.",
                    "status": "available",
                    "authority": "connected",
                    "permission": "read",
                    "data_scope": "Approved route origin and destination only",
                    "risk_class": "low",
                    "version": "1",
                    "source": "host:function.route-estimator",
                    "capabilities": ["calculate_route_estimate"],
                    "requires": ["capability.evidence-tracking"],
                    "conflicts_with": [],
                    "fallback": "capability.manual-handoff",
                },),
            },
        }
        proposal = execute(ExecutionEnvelope(**request))

        self.assertEqual("BLOCKED", proposal.state)
        self.assertEqual("ROUTING_PREVIEW", proposal.dashboard["active_stage"])
        self.assertEqual(
            ["function.route-estimator"],
            proposal.routing_preview["execution_sequence"],
        )
        self.assertEqual((), proposal.routing_decisions)

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("READY", approved.state)
        self.assertEqual("calculate", approved.active_unit)
        self.assertEqual("function", approved.routing_decisions[0]["provider_type"])
        self.assertEqual("function.route-estimator", approved.routing_decisions[0]["provider_id"])

    def test_unmatched_explicit_capability_requirement_blocks_execution(self) -> None:
        request = {
            "objective": "Calculate the governed route estimate",
            "task_id": "TASK-ROUTE-ESTIMATE",
            "plan_id": "plan-route-estimate",
            "work_units": (
                {"id": "calculate", "status": "PENDING", "dependencies": []},
            ),
            "capability_requirements": ("calculate_route_estimate",),
        }
        proposal = execute(ExecutionEnvelope(**request))

        self.assertEqual("BLOCKED", proposal.state)
        self.assertEqual(
            ["calculate_route_estimate"],
            proposal.routing_preview["unmatched_requirements"],
        )
        self.assertIn(
            "requirement:calculate_route_estimate:NO_ADMITTED_PROVIDER",
            proposal.routing_preview["unresolved_gates"],
        )

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("BLOCKED", approved.state)
        self.assertIsNone(approved.active_unit)
        self.assertEqual("ROUTING", approved.dashboard["active_stage"])
        self.assertNotIn("EXECUTION", approved.execution_trace)

    def test_cyclic_provider_prerequisites_fail_closed(self) -> None:
        provider = {
            "description": "Performs one half of a cyclic operation.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:test",
            "capabilities": ["cyclic_operation"],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        request = {
            "objective": "Run the governed cyclic operation",
            "task_id": "TASK-CYCLIC-OPERATION",
            "plan_id": "plan-cyclic-operation",
            "work_units": (
                {"id": "operate", "status": "PENDING", "dependencies": []},
            ),
            "capability_requirements": ("cyclic_operation",),
            "provider_inventory": {
                "function": (
                    {
                        **provider,
                        "id": "function.cycle-a",
                        "name": "Cycle A",
                        "requires": ["function.cycle-b"],
                    },
                    {
                        **provider,
                        "id": "function.cycle-b",
                        "name": "Cycle B",
                        "requires": ["function.cycle-a"],
                    },
                ),
            },
        }
        proposal = execute(ExecutionEnvelope(**request))

        self.assertEqual("BLOCKED", proposal.state)
        self.assertEqual(
            ["function.cycle-a", "function.cycle-b"],
            proposal.routing_preview["cyclic_provider_ids"],
        )
        self.assertEqual([], proposal.routing_preview["execution_sequence"])
        self.assertIn(
            "provider_dependency_cycle:function.cycle-a,function.cycle-b",
            proposal.routing_preview["unresolved_gates"],
        )

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("BLOCKED", approved.state)
        self.assertIsNone(approved.active_unit)
        self.assertEqual("ROUTING", approved.dashboard["active_stage"])
        self.assertEqual((), approved.routing_decisions)
        self.assertNotIn("EXECUTION", approved.execution_trace)

    def test_provider_version_and_source_are_bound_to_preview_digest(self) -> None:
        provider = {
            "id": "function.bound-provider",
            "name": "Bound provider",
            "description": "Executes a version-bound host operation.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:function.bound-provider@1",
            "capabilities": ["bound_operation"],
            "requires": [],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        request = {
            "objective": "Run the bound operation",
            "task_id": "TASK-BOUND-OPERATION",
            "plan_id": "plan-bound-operation",
            "work_units": ({"id": "run", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("bound_operation",),
        }
        proposal = execute(ExecutionEnvelope(
            **request,
            provider_inventory={"function": (provider,)},
        ))
        changed = {**provider, "version": "2", "source": "host:function.bound-provider@2"}

        result = execute(ExecutionEnvelope(
            **request,
            provider_inventory={"function": (changed,)},
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertNotEqual(
            proposal.routing_preview["digest"],
            result.routing_preview["digest"],
        )
        self.assertEqual("BLOCKED", result.state)
        self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])

    def test_pending_clarification_cannot_be_bypassed_by_routing_approval(self) -> None:
        request = {
            "objective": "Implement and test a repository change",
            "task_id": "TASK-PENDING-CLARIFICATION",
            "plan_id": "plan-pending-clarification",
            "work_units": ({"id": "implement", "status": "PENDING", "dependencies": []},),
            "surface": "codex",
            "clarification_status": "PENDING",
        }
        proposal = execute(ExecutionEnvelope(**request))
        result = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("BLOCKED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertNotIn("EXECUTION", result.execution_trace)

    def test_conflicting_providers_fail_closed_before_routing(self) -> None:
        base = {
            "description": "Provides one conflicting operation.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:test",
            "capabilities": ["conflicting_operation"],
            "requires": [],
            "fallback": "capability.manual-handoff",
        }
        request = {
            "objective": "Run the governed operation",
            "task_id": "TASK-CONFLICTING-OPERATION",
            "plan_id": "plan-conflicting-operation",
            "work_units": ({"id": "run", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("conflicting_operation",),
            "provider_inventory": {"function": (
                {**base, "id": "function.alpha", "name": "Alpha", "conflicts_with": ["function.beta"]},
                {**base, "id": "function.beta", "name": "Beta", "conflicts_with": []},
            )},
        }
        proposal = execute(ExecutionEnvelope(**request))
        self.assertEqual(
            [["function.alpha", "function.beta"]],
            proposal.routing_preview["conflicting_provider_pairs"],
        )

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))
        self.assertEqual("BLOCKED", approved.state)
        self.assertEqual((), approved.routing_decisions)
        self.assertNotIn("EXECUTION", approved.execution_trace)

    def test_missing_provider_prerequisite_returns_blocked_result(self) -> None:
        provider = {
            "id": "function.missing-prerequisite",
            "name": "Missing prerequisite",
            "description": "Requires an unavailable host capability.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:test",
            "capabilities": ["guarded_operation"],
            "requires": ["function.not-installed"],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        request = {
            "objective": "Run the guarded operation",
            "task_id": "TASK-GUARDED-OPERATION",
            "plan_id": "plan-guarded-operation",
            "work_units": ({"id": "run", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("guarded_operation",),
            "provider_inventory": {"function": (provider,)},
        }
        proposal = execute(ExecutionEnvelope(**request))
        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("BLOCKED", approved.state)
        self.assertEqual("ROUTING", approved.dashboard["active_stage"])
        self.assertEqual((), approved.routing_decisions)
        self.assertNotIn("EXECUTION", approved.execution_trace)

    def test_host_provider_prerequisite_is_previewed_and_routed_first(self) -> None:
        base = {
            "description": "Performs an admitted host operation.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:test",
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        request = {
            "objective": "Run the host operation",
            "task_id": "TASK-HOST-DEPENDENCY",
            "plan_id": "plan-host-dependency",
            "work_units": ({"id": "run", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("host_operation",),
            "provider_inventory": {
                "function": ({
                    **base,
                    "id": "function.host-operation",
                    "name": "Host operation",
                    "capabilities": ["host_operation"],
                    "requires": ["tool.host-dependency"],
                },),
                "tool": ({
                    **base,
                    "id": "tool.host-dependency",
                    "name": "Host dependency",
                    "capabilities": ["host_dependency"],
                    "requires": [],
                },),
            },
        }
        proposal = execute(ExecutionEnvelope(**request))

        self.assertEqual(
            ["tool.host-dependency", "function.host-operation"],
            proposal.routing_preview["execution_sequence"],
        )
        self.assertEqual([], proposal.routing_preview["missing_prerequisite_providers"])

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("READY", approved.state)
        self.assertEqual(
            ["tool.host-dependency", "function.host-operation"],
            [decision["provider_id"] for decision in approved.routing_decisions],
        )

    def test_explicitly_unavailable_host_provider_is_not_proposed(self) -> None:
        provider = {
            "id": "function.offline",
            "name": "Offline provider",
            "description": "Is registered but currently unavailable.",
            "status": "available",
            "available": False,
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:function.offline",
            "capabilities": ["offline_operation"],
            "requires": [],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        proposal = execute(ExecutionEnvelope(
            objective="Run the offline operation",
            task_id="TASK-OFFLINE",
            plan_id="plan-offline",
            work_units=({"id": "run", "status": "PENDING", "dependencies": []},),
            capability_requirements=("offline_operation",),
            provider_inventory={"function": (provider,)},
        ))

        self.assertEqual([], proposal.routing_preview["providers"])
        self.assertEqual(
            ["offline_operation"],
            proposal.routing_preview["unmatched_requirements"],
        )

        approved = execute(ExecutionEnvelope(
            objective="Run the offline operation",
            task_id="TASK-OFFLINE",
            plan_id="plan-offline",
            work_units=({"id": "run", "status": "PENDING", "dependencies": []},),
            capability_requirements=("offline_operation",),
            provider_inventory={"function": (provider,)},
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("BLOCKED", approved.state)
        self.assertEqual("ROUTING", approved.dashboard["active_stage"])
        self.assertEqual((), approved.routing_decisions)

    def test_host_domain_method_uses_governed_preview_and_handoff(self) -> None:
        source_commit = "a" * 40
        method = {
            "id": "domain-method.host-research",
            "name": "Host research method",
            "description": "Performs governed specialist research.",
            "status": "available",
            "authority": "specialist-contract",
            "permission": "read",
            "data_scope": "Approved task context and public sources only",
            "risk_class": "medium",
            "version": "1",
            "source": f"https://example.invalid/method/{source_commit}/contract.json",
            "source_commit": source_commit,
            "contract_sha256": "sha256:" + "b" * 64,
            "capabilities": ["host_specialist_research"],
            "requires": [],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
            "task_classes": ["RESEARCH"],
            "activation_authority": "ATLAS_OS",
            "consumer_id": "HOST-RESEARCH",
            "requires_domain_handoff": True,
            "accepted_handoff_states": ["PARTIAL", "READY"],
            "blocked_handoff_execution": True,
            "owns_execution_spine": False,
            "owns_planning": False,
            "owns_approvals": False,
        }
        request = {
            "objective": "Research the host specialist topic",
            "task_id": "TASK-HOST-METHOD",
            "plan_id": "plan-host-method",
            "work_units": ({"id": "research", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("host_specialist_research",),
            "provider_inventory": {"domain-method": (method,)},
            "timestamp": "2026-10-21T23:31:00+06:00",
            "timezone_name": "Asia/Dhaka",
        }
        proposal = execute(ExecutionEnvelope(**request))

        self.assertIn(
            "domain-method.host-research",
            proposal.routing_preview["execution_sequence"],
        )

        approved = execute(ExecutionEnvelope(
            **request,
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertEqual("READY", approved.state)
        decision = next(
            item for item in approved.routing_decisions
            if item["provider_id"] == "domain-method.host-research"
        )
        self.assertEqual("ROUTED", decision["status"])

    def test_host_tool_inventory_does_not_revalidate_built_in_tools_as_host_records(self) -> None:
        provider = {
            "id": "tool.host-estimator",
            "name": "Host estimator",
            "description": "Reads approved values and estimates a result.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved estimate inputs only",
            "risk_class": "low",
            "version": "1",
            "source": "host:tool.host-estimator",
            "capabilities": ["host_estimate"],
            "requires": [],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
        }
        result = execute(ExecutionEnvelope(
            objective="Estimate the approved values",
            task_id="TASK-HOST-ESTIMATE",
            plan_id="plan-host-estimate",
            work_units=({"id": "estimate", "status": "PENDING", "dependencies": []},),
            capability_requirements=("host_estimate",),
            provider_inventory={"tool": (provider,)},
        ))
        self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])

    def test_completed_plan_does_not_request_provider_approval_again(self) -> None:
        result = execute(ExecutionEnvelope(
            objective="Implement and test a repository change",
            task_id="TASK-COMPLETED-REPOSITORY-CHANGE",
            plan_id="plan-completed-repository-change",
            work_units=({"id": "implement", "status": "COMPLETED", "dependencies": []},),
            surface="codex",
        ))

        self.assertEqual("COMPLETED", result.state)
        self.assertIsNone(result.active_unit)
        self.assertEqual("NOT_REQUIRED", result.routing_preview["status"])
        self.assertNotIn("ROUTING_PREVIEW", result.execution_trace)

    def test_multilabel_task_uses_provider_compatible_routing_class(self) -> None:
        request = {
            "objective": (
                "Research and write a report on public procurement opportunities "
                "for Bangladesh Navy coastal surveillance radar"
            ),
            "task_id": "TASK-MULTILABEL-RADAR-RESEARCH",
            "plan_id": "plan-multilabel-radar-research",
            "work_units": ({"id": "research", "status": "PENDING", "dependencies": []},),
            "surface": "chatgpt",
            "clarification_status": "RESOLVED",
            "timestamp": "2026-10-21T23:31:00+06:00",
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
        self.assertIn("RESEARCH", result.task_classes)
        self.assertEqual("BLOCKED", argus["status"])
        self.assertEqual("HANDOFF_STATE_NOT_ACCEPTED", argus["reason"])
        self.assertNotIn("EXECUTION", result.execution_trace)

    def test_provider_task_class_change_invalidates_preview_approval(self) -> None:
        provider = {
            "id": "function.class-bound",
            "name": "Class-bound provider",
            "description": "Runs under an explicitly selected task class.",
            "status": "available",
            "authority": "connected",
            "permission": "read",
            "data_scope": "Approved task input only",
            "risk_class": "low",
            "version": "1",
            "source": "host:function.class-bound@1",
            "capabilities": ["class_bound_operation"],
            "requires": [],
            "conflicts_with": [],
            "fallback": "capability.manual-handoff",
            "task_classes": ["DOCUMENT"],
        }
        request = {
            "objective": "Research and write a report using the class-bound operation",
            "task_id": "TASK-CLASS-BOUND",
            "plan_id": "plan-class-bound",
            "work_units": ({"id": "run", "status": "PENDING", "dependencies": []},),
            "capability_requirements": ("class_bound_operation",),
        }
        proposal = execute(ExecutionEnvelope(
            **request,
            provider_inventory={"function": (provider,)},
        ))
        proposed_provider = proposal.routing_preview["providers"][0]
        self.assertEqual(["DOCUMENT"], proposed_provider["task_classes"])
        self.assertEqual("DOCUMENT", proposed_provider["routing_task_class"])

        changed = {**provider, "task_classes": ["RESEARCH"]}
        result = execute(ExecutionEnvelope(
            **request,
            provider_inventory={"function": (changed,)},
            routing_approval_status="APPROVED",
            routing_preview_digest=proposal.routing_preview["digest"],
        ))

        self.assertNotEqual(
            proposal.routing_preview["digest"],
            result.routing_preview["digest"],
        )
        self.assertEqual("BLOCKED", result.state)
        self.assertEqual("ROUTING_PREVIEW", result.dashboard["active_stage"])

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
