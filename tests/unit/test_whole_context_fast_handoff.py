from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from atlas_runtime import ExecutionContext, prepare_domain_context_handoff, verify_domain_context_handoff

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / "spec/semantic-normalization.yaml"
HANDOFF_SPEC = ROOT / "spec/domain-handoff.yaml"
SPINE = ROOT / "spec/execution-spine.yaml"
RADAR_EXAMPLE = ROOT / "examples/workflows/coastal-surveillance-radar-bangladesh-navy.json"


class WholeContextFastHandoffTests(unittest.TestCase):
    def _execution_context(self) -> ExecutionContext:
        return ExecutionContext(
            task_id="TASK-WHOLE-CONTEXT-001",
            plan_id="plan-whole-context",
            work_unit_id="unit-argus-collection",
            task_class="RESEARCH",
        )

    def test_semantic_contract_requires_whole_context_before_decomposition(self) -> None:
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        self.assertTrue(contract["whole_context_before_decomposition"])
        self.assertTrue(contract["context_precedes_classification"])
        self.assertTrue(contract["decomposition_must_preserve_relationships"])
        self.assertTrue(contract["reconcile_decomposed_context_to_whole"])
        self.assertEqual(
            [
                "PRESERVE_WHOLE_CONTEXT",
                "UNDERSTAND_WHOLE_CONTEXT",
                "NORMALIZE_WHOLE_CONTEXT",
                "DECOMPOSE_AS_REQUIRED",
                "CLASSIFY_HIGH_CONFIDENCE_CONTEXT",
                "RECONCILE_TO_WHOLE_CONTEXT",
                "HANDOFF_WITH_UNRESOLVED_CONTEXT",
            ],
            contract["fast_path_sequence"],
        )

    def test_semantic_contract_is_non_blocking_for_downstream_unknowns(self) -> None:
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        self.assertTrue(contract["fast_path"]["prefer_local_governed_context"])
        self.assertTrue(contract["fast_path"]["no_research_loop_for_normalization"])
        self.assertTrue(contract["fast_path"]["downstream_unknowns_do_not_block_handoff"])
        self.assertEqual(
            "meaning_ambiguity",
            contract["fast_path"]["only_semantic_blocker"],
        )
        for item in (
            "lifecycle_stage",
            "procurement_route",
            "budget",
            "quantity",
            "technical_specification",
            "exact_classification_code",
            "specific_standard_applicability",
            "supplier_or_oem",
        ):
            self.assertIn(item, contract["defer_to_downstream"])

    def test_handoff_is_ready_when_meaning_is_clear_even_if_alignment_needs_research(self) -> None:
        task = {
            "id": "TASK-WHOLE-CONTEXT-001",
            "semantic_context": {
                "status": "READY",
                "original_input": "coastal surveillance radar for Bangladesh navy",
                "normalized_input": "Coastal Surveillance Radar for the Bangladesh Navy",
                "meaning_ambiguities": [],
                "unresolved_context": ["lifecycle-stage", "exact-hs-code", "specific-standard-applicability"],
            },
            "domain_classification": {
                "status": "PARTIAL",
                "facets": {},
                "taxonomy_references": [],
                "risk_flags": ["defense"],
                "unresolved_facets": ["lifecycle-stage", "exact-hs-code"],
                "conditional_candidates": [],
                "evidence": [],
                "next_action": None,
            },
            "domain_alignment": {
                "domains": ["defense", "maritime-surveillance", "radar-systems"],
                "status": "RESEARCH_REQUIRED",
                "frameworks": [],
                "applicability": {"reason": "Exact standards applicability may be resolved downstream."},
                "deviations": [],
                "compliance": "NOT_CLAIMED",
                "evidence": [],
            },
        }
        handoff = prepare_domain_context_handoff(
            task,
            execution_context=self._execution_context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-WHOLE-CONTEXT",
            created_at="2026-10-22T15:45:00+06:00",
        )
        self.assertEqual("READY", handoff["state"])
        self.assertEqual(task["semantic_context"], handoff["semantic_context"])
        self.assertIn("lifecycle-stage", handoff["unresolved_material"])
        self.assertIn("specific-standard-applicability", handoff["unresolved_material"])
        self.assertTrue(verify_domain_context_handoff(handoff))

    def test_handoff_blocks_only_when_meaning_itself_is_ambiguous(self) -> None:
        task = {
            "id": "TASK-WHOLE-CONTEXT-001",
            "semantic_context": {
                "status": "AMBIGUOUS",
                "original_input": "radar for bank",
                "normalized_input": "radar for bank",
                "meaning_ambiguities": ["bank could identify an organization, financial institution, or geographic river bank"],
                "unresolved_context": [],
            },
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
            execution_context=self._execution_context(),
            consumer="ARGUS",
            handoff_id="HANDOFF-ARGUS-AMBIGUOUS",
            created_at="2026-10-22T15:45:00+06:00",
        )
        self.assertEqual("BLOCKED", handoff["state"])

    def test_specs_and_example_reflect_fast_non_blocking_handoff(self) -> None:
        handoff_spec = HANDOFF_SPEC.read_text(encoding="utf-8").lower()
        spine = SPINE.read_text(encoding="utf-8").lower()
        example = json.loads(RADAR_EXAMPLE.read_text(encoding="utf-8"))
        self.assertIn("meaning ambiguity", handoff_spec)
        self.assertIn("downstream unknown", handoff_spec)
        self.assertIn("whole context", spine)
        self.assertNotEqual("BLOCKED", example["status"])
        self.assertNotEqual("RESEARCH_REQUIRED", example["domain_alignment"]["status"])
        self.assertNotIn("lifecycle-stage", example["domain_classification"]["unresolved_facets"])


if __name__ == "__main__":
    unittest.main()
