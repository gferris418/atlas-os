from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum


class NodeKind(str, Enum):
    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    OPTIONAL = "OPTIONAL"


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SKIPPED_WITH_AUTHORITY = "SKIPPED_WITH_AUTHORITY"
    SUPERSEDED = "SUPERSEDED"


_RESOLVED_DEPENDENCY_STATUSES = {
    NodeStatus.COMPLETE,
    NodeStatus.NOT_APPLICABLE,
    NodeStatus.SKIPPED_WITH_AUTHORITY,
    NodeStatus.SUPERSEDED,
}


@dataclass(frozen=True)
class ExecutionNode:
    stable_id: str
    serial: str
    title: str
    parent_id: str | None = None
    dependencies: tuple[str, ...] = ()
    kind: NodeKind = NodeKind.REQUIRED

    def __post_init__(self) -> None:
        if not self.stable_id.strip():
            raise ValueError("stable_id must be non-empty")
        if not self.serial.strip():
            raise ValueError("serial must be non-empty")
        if not self.title.strip():
            raise ValueError("title must be non-empty")
        if any(not dependency.strip() for dependency in self.dependencies):
            raise ValueError("dependencies must contain non-empty stable IDs")


@dataclass(frozen=True)
class ExecutionObservation:
    stable_id: str
    serial: str
    status: NodeStatus


@dataclass(frozen=True)
class ReconciliationReport:
    valid: bool
    missing_ids: tuple[str, ...]
    unknown_ids: tuple[str, ...]
    duplicate_ids: tuple[str, ...]
    serial_mismatches: tuple[str, ...]


class ExecutionState:
    def __init__(self, graph: ExecutionGraph, execution_id: str) -> None:
        if not execution_id.strip():
            raise ValueError("execution_id must be non-empty")
        self._graph = graph
        self.execution_id = execution_id
        self._statuses = {
            node.stable_id: NodeStatus.PENDING for node in graph.nodes
        }

    def status(self, stable_id: str) -> NodeStatus:
        self._graph.node(stable_id)
        return self._statuses[stable_id]

    def set_status(self, stable_id: str, status: NodeStatus) -> None:
        node = self._graph.node(stable_id)
        if status in _RESOLVED_DEPENDENCY_STATUSES:
            unresolved = tuple(
                dependency
                for dependency in node.dependencies
                if self._statuses[dependency] not in _RESOLVED_DEPENDENCY_STATUSES
            )
            if unresolved:
                raise ValueError(
                    f"unresolved dependencies for {stable_id}: {', '.join(unresolved)}"
                )
        if status is NodeStatus.NOT_APPLICABLE and node.kind is NodeKind.REQUIRED:
            raise ValueError("required nodes cannot be marked NOT_APPLICABLE")
        self._statuses[stable_id] = status


class ExecutionGraph:
    def __init__(
        self,
        *,
        workflow_id: str,
        version: str,
        nodes: tuple[ExecutionNode, ...],
    ) -> None:
        if not workflow_id.strip():
            raise ValueError("workflow_id must be non-empty")
        if not version.strip():
            raise ValueError("version must be non-empty")
        self.workflow_id = workflow_id
        self.version = version
        self.nodes = tuple(nodes)
        self._nodes = self._validate_nodes(self.nodes)
        self.fingerprint = self._build_fingerprint()

    def node(self, stable_id: str) -> ExecutionNode:
        try:
            return self._nodes[stable_id]
        except KeyError as exc:
            raise KeyError(f"unknown stable_id {stable_id}") from exc

    def new_state(self, execution_id: str) -> ExecutionState:
        return ExecutionState(self, execution_id)

    def reconcile(
        self, observations: tuple[ExecutionObservation, ...]
    ) -> ReconciliationReport:
        canonical_ids = set(self._nodes)
        observed_ids = [observation.stable_id for observation in observations]
        counts = Counter(observed_ids)
        observed_set = set(observed_ids)

        missing_ids = tuple(sorted(canonical_ids - observed_set))
        unknown_ids = tuple(sorted(observed_set - canonical_ids))
        duplicate_ids = tuple(sorted(stable_id for stable_id, count in counts.items() if count > 1))
        serial_mismatches = tuple(
            sorted(
                stable_id
                for stable_id in canonical_ids & observed_set
                if any(
                    observation.stable_id == stable_id
                    and observation.serial != self._nodes[stable_id].serial
                    for observation in observations
                )
            )
        )
        valid = not (missing_ids or unknown_ids or duplicate_ids or serial_mismatches)
        return ReconciliationReport(
            valid=valid,
            missing_ids=missing_ids,
            unknown_ids=unknown_ids,
            duplicate_ids=duplicate_ids,
            serial_mismatches=serial_mismatches,
        )

    def _validate_nodes(self, nodes: tuple[ExecutionNode, ...]) -> dict[str, ExecutionNode]:
        by_id: dict[str, ExecutionNode] = {}
        serials: set[str] = set()
        for node in nodes:
            if node.stable_id in by_id:
                raise ValueError(f"duplicate stable_id {node.stable_id}")
            if node.serial in serials:
                raise ValueError(f"duplicate serial {node.serial}")
            by_id[node.stable_id] = node
            serials.add(node.serial)

        for node in nodes:
            if node.parent_id is not None:
                parent = by_id.get(node.parent_id)
                if parent is None:
                    raise ValueError(f"unknown parent {node.parent_id}")
                expected_prefix = f"{parent.serial}."
                if not node.serial.startswith(expected_prefix):
                    raise ValueError(
                        f"parent serial mismatch for {node.stable_id}: "
                        f"expected prefix {expected_prefix}"
                    )
            for dependency in node.dependencies:
                if dependency not in by_id:
                    raise ValueError(
                        f"unknown dependency {dependency} for {node.stable_id}"
                    )

        self._validate_contiguous_siblings(nodes, by_id)
        self._validate_dependency_cycles(nodes, by_id)
        return by_id

    @staticmethod
    def _validate_contiguous_siblings(
        nodes: tuple[ExecutionNode, ...], by_id: dict[str, ExecutionNode]
    ) -> None:
        siblings: dict[str | None, list[ExecutionNode]] = defaultdict(list)
        for node in nodes:
            siblings[node.parent_id].append(node)

        for parent_id, group in siblings.items():
            positions: list[int] = []
            for node in group:
                segment = node.serial.rsplit(".", maxsplit=1)[-1]
                if not segment.isdigit() or int(segment) < 1:
                    raise ValueError(f"serial segment must be a positive integer: {node.serial}")
                positions.append(int(segment))
            expected = list(range(1, len(group) + 1))
            if sorted(positions) != expected:
                context = "top-level" if parent_id is None else by_id[parent_id].stable_id
                raise ValueError(
                    f"missing serial in {context}: expected {expected}, observed {sorted(positions)}"
                )

    @staticmethod
    def _validate_dependency_cycles(
        nodes: tuple[ExecutionNode, ...], by_id: dict[str, ExecutionNode]
    ) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(stable_id: str) -> None:
            if stable_id in visiting:
                raise ValueError(f"dependency cycle detected at {stable_id}")
            if stable_id in visited:
                return
            visiting.add(stable_id)
            for dependency in by_id[stable_id].dependencies:
                visit(dependency)
            visiting.remove(stable_id)
            visited.add(stable_id)

        for node in nodes:
            visit(node.stable_id)

    def _build_fingerprint(self) -> str:
        payload = {
            "workflow_id": self.workflow_id,
            "version": self.version,
            "nodes": [
                {
                    "stable_id": node.stable_id,
                    "serial": node.serial,
                    "title": node.title,
                    "parent_id": node.parent_id,
                    "dependencies": list(node.dependencies),
                    "kind": node.kind.value,
                }
                for node in sorted(self.nodes, key=lambda item: item.serial)
            ],
        }
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "ExecutionGraph",
    "ExecutionNode",
    "ExecutionObservation",
    "ExecutionState",
    "NodeKind",
    "NodeStatus",
    "ReconciliationReport",
]
