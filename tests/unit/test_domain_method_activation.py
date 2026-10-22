from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from atlas_runtime import ExecutionContext, prepare_domain_context_handoff, route_domain_method


ROOT = Path(__file__).resolve().parents[2]


class DomainMethodActivationTests(unittest.TestCase):
    def _context(self, *, task_id: str = "TASK-ARGUS-ACTIVATION") -> ExecutionContext:
        return ExecutionContext(
            task_id=task_id,
            plan_id="plan-argus-activation",
            work_unit_id="unit-argus-analysis",
            task_class="ANALYSIS",
            available_capabilities=frozenset({
                "capability.domain-alignment",
                "capability.evidence-tracking",
            }),
        )

    def _registry(self) -> dict:
        return yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text())

    def _method(self) -> dict:
        return self._registry()["items"][0]

    def _handoff(self, *, state: str = "READY", consumer: str = "ARGUS") -> dict:
        ambiguous = state == "BLOCKED"
        unresolved = ["procurement-route"] if state == "DOWNSTREAM_UNRESOLVED" else []
        task = {
            "id": "TASK-ARGUS-ACTIVATION",
            "semantic_context": {
                "status": "AMBIGUOUS" if ambiguous else "READY",
                "original_input": "coastal surveillance radar for Bangladesh navy" if not ambiguous else "radar for bank",
                "normalized_input": "Coastal Surveillance Radar for the Bangladesh Navy" if not ambiguous else "radar for bank",
                "whole_context_summary": None,
                "normalization_notes": [],
                "meaning_ambiguities": ["meaning is ambiguous"] if ambiguous else [],
                "unresolved_context": unresolved,
            },
            "domain_classification": {
                "status": "PARTIAL" if unresolved else "CLASSIFIED",
                "facets": {},
                "taxonomy_references": [],
                "risk_flags": [],
                "unresolved_facets": unresolved,
                "conditional_candidates": [],
                "evidence": [],
                "next_action": None,
            },
            "domain_alignment": {
                "domains": ["government-opportunity-intelligence"],
                "status": "RESEARCH_REQUIRED" if unresolved else "ALIGNED",
                "frameworks": [],
                "applicability": {},
                "deviations": [],
                "compliance": "NOT_CLAIMED",
                "evidence": [],
            },
        }
        return prepare_domain_context_handoff(
            task,
            execution_context=self._context(),
            consumer=consumer,
            handoff_id=f"HANDOFF-ARGUS-{state}",
            created_at="2026-10-18T12:00:00+06:00",
        )

    def test_argus_activates_only_for_explicit_structured_capability(self) -> None:
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            self._registry(),
            execution_context=self._context(),
            handoff=self._handoff(),
        )
        self.assertEqual("ACTIVATE", decision["status"])
        self.assertEqual("domain-method.argus-intelligence", decision["method_id"])

    def test_generic_question_does_not_implicitly_activate_argus(self) -> None:
        with self.assertRaisesRegex(LookupError, "no available domain method"):
            route_domain_method(
                "general_factual_answer",
                self._registry(),
                execution_context=self._context(),
                handoff=self._handoff(),
            )

    def test_missing_or_semantically_ambiguous_handoff_blocks_dependent_activation(self) -> None:
        missing = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            self._registry(),
            execution_context=self._context(),
        )
        self.assertEqual({"status": "BLOCKED", "reason": "HANDOFF_REQUIRED", "method_id": "domain-method.argus-intelligence"}, missing)

        blocked = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            self._registry(),
            execution_context=self._context(),
            handoff=self._handoff(state="BLOCKED"),
        )
        self.assertEqual("BLOCKED", blocked["status"])
        self.assertEqual("HANDOFF_STATE_NOT_ACCEPTED", blocked["reason"])

    def test_unresolved_downstream_context_does_not_block_argus(self) -> None:
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            self._registry(),
            execution_context=self._context(),
            handoff=self._handoff(state="DOWNSTREAM_UNRESOLVED"),
        )
        self.assertEqual("ACTIVATE", decision["status"])
        self.assertEqual(["procurement-route"], decision["unresolved_material"])

    def test_external_registration_cannot_opt_into_blocked_execution(self) -> None:
        method = self._method()
        method["accepted_handoff_states"].append("BLOCKED")
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            {**self._registry(), "items": [method]},
            execution_context=self._context(),
            handoff=self._handoff(state="BLOCKED"),
        )
        self.assertEqual("BLOCKED", decision["status"])
        self.assertEqual("HANDOFF_STATE_NOT_ACCEPTED", decision["reason"])

    def test_domain_method_cannot_claim_atlas_governance_ownership(self) -> None:
        method = self._method()
        self.assertEqual("ATLAS_OS", method["activation_authority"])
        self.assertFalse(method["owns_execution_spine"])
        self.assertFalse(method["owns_planning"])
        self.assertFalse(method["owns_approvals"])

    def test_cross_execution_context_handoff_replay_is_blocked(self) -> None:
        contexts = {
            "task_id": self._context(task_id="TASK-DIFFERENT-CONTEXT"),
            "plan_id": ExecutionContext(
                task_id="TASK-ARGUS-ACTIVATION", plan_id="plan-different",
                work_unit_id="unit-argus-analysis", task_class="ANALYSIS",
                available_capabilities=self._context().available_capabilities,
            ),
            "work_unit_id": ExecutionContext(
                task_id="TASK-ARGUS-ACTIVATION", plan_id="plan-argus-activation",
                work_unit_id="unit-different", task_class="ANALYSIS",
                available_capabilities=self._context().available_capabilities,
            ),
        }
        for field_name, context in contexts.items():
            with self.subTest(field_name=field_name):
                decision = route_domain_method(
                    "government_public_sector_opportunity_intelligence",
                    self._registry(),
                    execution_context=context,
                    handoff=self._handoff(),
                )
                self.assertEqual("BLOCKED", decision["status"])
                self.assertEqual("HANDOFF_EXECUTION_CONTEXT_MISMATCH", decision["reason"])
                self.assertEqual([field_name], decision["mismatches"])

    def test_denied_domain_method_cannot_activate(self) -> None:
        method = self._method()
        method["permission"] = "denied"
        with self.assertRaisesRegex(LookupError, "no available domain method"):
            route_domain_method(
                "government_public_sector_opportunity_intelligence",
                {**self._registry(), "items": [method]},
                execution_context=self._context(),
                handoff=self._handoff(),
            )

    def test_missing_prerequisite_or_active_conflict_cannot_activate(self) -> None:
        with self.assertRaisesRegex(LookupError, "no available domain method"):
            route_domain_method(
                "government_public_sector_opportunity_intelligence",
                self._registry(),
                execution_context=ExecutionContext(
                    task_id="TASK-ARGUS-ACTIVATION",
                    plan_id="plan-argus-activation",
                    work_unit_id="unit-argus-analysis",
                    task_class="ANALYSIS",
                ),
                handoff=self._handoff(),
            )

        method = self._method()
        method["conflicts_with"] = ["capability.active-conflict"]
        with self.assertRaisesRegex(LookupError, "no available domain method"):
            route_domain_method(
                "government_public_sector_opportunity_intelligence",
                {**self._registry(), "items": [method]},
                execution_context=ExecutionContext(
                    task_id="TASK-ARGUS-ACTIVATION",
                    plan_id="plan-argus-activation",
                    work_unit_id="unit-argus-analysis",
                    task_class="ANALYSIS",
                    available_capabilities=self._context().available_capabilities,
                    active_capabilities=frozenset({"capability.active-conflict"}),
                ),
                handoff=self._handoff(),
            )

    def test_domain_method_cannot_disable_governed_handoff(self) -> None:
        for field in ("requires_domain_handoff", "blocked_handoff_execution"):
            method = self._method()
            method[field] = False
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "governed handoff"):
                route_domain_method(
                    "government_public_sector_opportunity_intelligence",
                    {**self._registry(), "items": [method]},
                    execution_context=self._context(),
                    handoff=None,
                )

    def test_inactive_registry_cannot_route_domain_method(self) -> None:
        registry = self._registry()
        registry["registry"]["status"] = "draft"
        with self.assertRaisesRegex(LookupError, "registry is not active"):
            route_domain_method(
                "government_public_sector_opportunity_intelligence",
                registry,
                execution_context=self._context(),
                handoff=self._handoff(),
            )


if __name__ == "__main__":
    unittest.main()
