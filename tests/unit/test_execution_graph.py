from __future__ import annotations

import unittest

from atlas_runtime.execution_graph import (
    Criticality,
    ExecutionGraph,
    ExecutionNode,
    ExecutionObservation,
    NodeKind,
    NodeStatus,
)


class ExecutionGraphTests(unittest.TestCase):
    def test_rejects_missing_serial_between_siblings(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing serial"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),
                    ExecutionNode("ATLAS-NORMALIZE", "03", "Normalize mission"),
                ),
            )

    def test_rejects_duplicate_stable_id_or_serial(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate stable_id"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),
                    ExecutionNode("ATLAS-INTAKE", "02", "Duplicate identity"),
                ),
            )

        with self.assertRaisesRegex(ValueError, "duplicate serial"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),
                    ExecutionNode("ATLAS-NORMALIZE", "01", "Normalize mission"),
                ),
            )

    def test_rejects_unknown_dependency_and_cycles(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode(
                        "ATLAS-INTAKE",
                        "01",
                        "Mission intake",
                        dependencies=("ATLAS-NOT-DEFINED",),
                    ),
                ),
            )

        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode(
                        "ATLAS-INTAKE",
                        "01",
                        "Mission intake",
                        dependencies=("ATLAS-NORMALIZE",),
                    ),
                    ExecutionNode(
                        "ATLAS-NORMALIZE",
                        "02",
                        "Normalize mission",
                        dependencies=("ATLAS-INTAKE",),
                    ),
                ),
            )

    def test_subitems_are_contiguous_and_parent_aligned(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.0",
            nodes=(
                ExecutionNode("ATLAS-CLASSIFY", "01", "Classification"),
                ExecutionNode(
                    "ATLAS-CLASSIFY-SECTOR",
                    "01.01",
                    "Sector classification",
                    parent_id="ATLAS-CLASSIFY",
                ),
                ExecutionNode(
                    "ATLAS-CLASSIFY-INDUSTRY",
                    "01.02",
                    "Industry classification",
                    parent_id="ATLAS-CLASSIFY",
                ),
            ),
        )
        self.assertEqual("ATLAS-CLASSIFY", graph.node("ATLAS-CLASSIFY-SECTOR").parent_id)

        with self.assertRaisesRegex(ValueError, "parent serial"):
            ExecutionGraph(
                workflow_id="ATLAS-BI-MISSION",
                version="1.0.0",
                nodes=(
                    ExecutionNode("ATLAS-CLASSIFY", "01", "Classification"),
                    ExecutionNode(
                        "ATLAS-CLASSIFY-SECTOR",
                        "02.01",
                        "Sector classification",
                        parent_id="ATLAS-CLASSIFY",
                    ),
                ),
            )

    def test_dependency_blocks_completion_until_predecessor_resolved(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.0",
            nodes=(
                ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),
                ExecutionNode(
                    "ATLAS-NORMALIZE",
                    "02",
                    "Normalize mission",
                    dependencies=("ATLAS-INTAKE",),
                ),
            ),
        )
        state = graph.new_state("MSN-001")

        with self.assertRaisesRegex(ValueError, "unresolved dependencies"):
            state.set_status("ATLAS-NORMALIZE", NodeStatus.COMPLETE)

        state.set_status("ATLAS-INTAKE", NodeStatus.COMPLETE)
        state.set_status("ATLAS-NORMALIZE", NodeStatus.COMPLETE)
        self.assertEqual(NodeStatus.COMPLETE, state.status("ATLAS-NORMALIZE"))

    def test_not_applicable_preserves_conditional_step_and_unblocks_dependency(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ARGUS-360-BI",
            version="1.0.0",
            nodes=(
                ExecutionNode(
                    "ARGUS-DEVELOPMENT-PARTNER",
                    "01",
                    "Development partner intelligence",
                    kind=NodeKind.CONDITIONAL,
                ),
                ExecutionNode(
                    "ARGUS-FUNDING-ASSESSMENT",
                    "02",
                    "Funding assessment",
                    dependencies=("ARGUS-DEVELOPMENT-PARTNER",),
                ),
            ),
        )
        state = graph.new_state("MSN-002")
        state.set_status("ARGUS-DEVELOPMENT-PARTNER", NodeStatus.NOT_APPLICABLE)
        state.set_status("ARGUS-FUNDING-ASSESSMENT", NodeStatus.COMPLETE)

        self.assertEqual(NodeStatus.NOT_APPLICABLE, state.status("ARGUS-DEVELOPMENT-PARTNER"))
        self.assertEqual(NodeStatus.COMPLETE, state.status("ARGUS-FUNDING-ASSESSMENT"))

    def test_node_governance_metadata_is_retained_and_fingerprinted(self) -> None:
        node = ExecutionNode(
            "ARGUS-GRADE-EVIDENCE",
            "01",
            "Grade evidence",
            owner="ARGUS",
            criticality=Criticality.CRITICAL,
            condition="evidence_collected",
            input_schema_ref="schemas/evidence-input.json",
            output_schema_ref="schemas/evidence-grade.json",
            evidence_requirement="At least one authoritative source",
            allowed_statuses=(
                NodeStatus.PENDING,
                NodeStatus.ACTIVE,
                NodeStatus.COMPLETE,
                NodeStatus.BLOCKED,
                NodeStatus.FAILED,
            ),
        )
        graph = ExecutionGraph(
            workflow_id="ARGUS-360-BI",
            version="1.1.0",
            nodes=(node,),
        )
        changed = ExecutionGraph(
            workflow_id="ARGUS-360-BI",
            version="1.1.0",
            nodes=(
                ExecutionNode(
                    "ARGUS-GRADE-EVIDENCE",
                    "01",
                    "Grade evidence",
                    owner="ARGUS",
                    criticality=Criticality.MAJOR,
                    condition="evidence_collected",
                    input_schema_ref="schemas/evidence-input.json",
                    output_schema_ref="schemas/evidence-grade.json",
                    evidence_requirement="At least one authoritative source",
                    allowed_statuses=node.allowed_statuses,
                ),
            ),
        )

        self.assertEqual("ARGUS", graph.node("ARGUS-GRADE-EVIDENCE").owner)
        self.assertEqual(Criticality.CRITICAL, graph.node("ARGUS-GRADE-EVIDENCE").criticality)
        self.assertNotEqual(graph.fingerprint, changed.fingerprint)

    def test_runtime_rejects_status_not_allowed_by_node_contract(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ATLAS-DECISION",
            version="1.0.0",
            nodes=(
                ExecutionNode(
                    "ATLAS-DECISION-GATE",
                    "01",
                    "Decision gate",
                    owner="ATLAS_OS",
                    allowed_statuses=(
                        NodeStatus.PENDING,
                        NodeStatus.ACTIVE,
                        NodeStatus.COMPLETE,
                        NodeStatus.BLOCKED,
                    ),
                ),
            ),
        )
        state = graph.new_state("MSN-003")

        with self.assertRaisesRegex(ValueError, "status FAILED is not allowed"):
            state.set_status("ATLAS-DECISION-GATE", NodeStatus.FAILED)

    def test_required_metadata_can_be_enforced_at_graph_construction(self) -> None:
        with self.assertRaisesRegex(ValueError, "owner must be non-empty"):
            ExecutionGraph(
                workflow_id="ATLAS-DECISION",
                version="1.0.0",
                nodes=(
                    ExecutionNode(
                        "ATLAS-DECISION-GATE",
                        "01",
                        "Decision gate",
                        owner="",
                    ),
                ),
            )

    def test_reconciliation_detects_missing_unknown_duplicate_and_serial_mismatch(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.0",
            nodes=(
                ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),
                ExecutionNode("ATLAS-NORMALIZE", "02", "Normalize mission"),
            ),
        )
        report = graph.reconcile(
            (
                ExecutionObservation("ATLAS-INTAKE", "99", NodeStatus.COMPLETE),
                ExecutionObservation("ATLAS-INTAKE", "01", NodeStatus.COMPLETE),
                ExecutionObservation("ATLAS-INVENTED", "03", NodeStatus.COMPLETE),
            )
        )

        self.assertFalse(report.valid)
        self.assertEqual(("ATLAS-NORMALIZE",), report.missing_ids)
        self.assertEqual(("ATLAS-INVENTED",), report.unknown_ids)
        self.assertEqual(("ATLAS-INTAKE",), report.duplicate_ids)
        self.assertEqual(("ATLAS-INTAKE",), report.serial_mismatches)

    def test_manifest_fingerprint_is_stable_and_sensitive_to_structure(self) -> None:
        graph = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.0",
            nodes=(ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),),
        )
        same = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.0",
            nodes=(ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),),
        )
        changed = ExecutionGraph(
            workflow_id="ATLAS-BI-MISSION",
            version="1.0.1",
            nodes=(ExecutionNode("ATLAS-INTAKE", "01", "Mission intake"),),
        )

        self.assertEqual(graph.fingerprint, same.fingerprint)
        self.assertNotEqual(graph.fingerprint, changed.fingerprint)


if __name__ == "__main__":
    unittest.main()
