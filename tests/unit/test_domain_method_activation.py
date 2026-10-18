from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from atlas_runtime import prepare_domain_context_handoff, route_domain_method


ROOT = Path(__file__).resolve().parents[2]


class DomainMethodActivationTests(unittest.TestCase):
    def _method(self) -> dict:
        registry = yaml.safe_load((ROOT / "registries/domain-methods.yaml").read_text())
        return registry["items"][0]

    def _handoff(self, *, state: str = "READY", consumer: str = "ARGUS") -> dict:
        classification_status = "CLASSIFIED" if state == "READY" else "PARTIAL"
        alignment_status = "ALIGNED"
        if state == "BLOCKED":
            alignment_status = "RESEARCH_REQUIRED"
        task = {
            "id": "TASK-ARGUS-ACTIVATION",
            "domain_classification": {
                "status": classification_status,
                "facets": {},
                "taxonomy_references": [],
                "risk_flags": [],
                "unresolved_facets": [] if state == "READY" else ["procurement-route"],
                "conditional_candidates": [],
                "evidence": [],
                "next_action": None,
            },
            "domain_alignment": {
                "domains": ["government-opportunity-intelligence"],
                "status": alignment_status,
                "frameworks": [],
                "applicability": {},
                "deviations": [],
                "compliance": "NOT_CLAIMED",
                "evidence": [],
            },
        }
        return prepare_domain_context_handoff(
            task,
            consumer=consumer,
            handoff_id=f"HANDOFF-ARGUS-{state}",
            created_at="2026-10-18T12:00:00+06:00",
        )

    def test_argus_activates_only_for_explicit_structured_capability(self) -> None:
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            [self._method()],
            handoff=self._handoff(),
        )
        self.assertEqual("ACTIVATE", decision["status"])
        self.assertEqual("domain-method.argus-intelligence", decision["method_id"])

    def test_generic_question_does_not_implicitly_activate_argus(self) -> None:
        with self.assertRaisesRegex(LookupError, "no available domain method"):
            route_domain_method("general_factual_answer", [self._method()], handoff=self._handoff())

    def test_missing_or_blocked_handoff_blocks_dependent_activation(self) -> None:
        missing = route_domain_method(
            "government_public_sector_opportunity_intelligence", [self._method()]
        )
        self.assertEqual({"status": "BLOCKED", "reason": "HANDOFF_REQUIRED", "method_id": "domain-method.argus-intelligence"}, missing)

        blocked = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            [self._method()],
            handoff=self._handoff(state="BLOCKED"),
        )
        self.assertEqual("BLOCKED", blocked["status"])
        self.assertEqual("HANDOFF_STATE_NOT_ACCEPTED", blocked["reason"])

    def test_partial_handoff_may_activate_with_unresolved_context_preserved(self) -> None:
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            [self._method()],
            handoff=self._handoff(state="PARTIAL"),
        )
        self.assertEqual("ACTIVATE", decision["status"])
        self.assertEqual(["procurement-route"], decision["unresolved_material"])

    def test_external_registration_cannot_opt_into_blocked_execution(self) -> None:
        method = self._method()
        method["accepted_handoff_states"].append("BLOCKED")
        decision = route_domain_method(
            "government_public_sector_opportunity_intelligence",
            [method],
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


if __name__ == "__main__":
    unittest.main()
