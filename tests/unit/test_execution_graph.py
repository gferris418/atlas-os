from __future__ import annotations

import unittest

from atlas_runtime.execution_graph import (
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
