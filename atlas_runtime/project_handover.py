from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum


class HandoverItemStatus(str, Enum):
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class HandoverItem:
    item_id: str
    description: str
    owner: str
    required: bool
    status: HandoverItemStatus = HandoverItemStatus.OPEN
    evidence_ref: str | None = None


@dataclass(frozen=True)
class ContractVariance:
    variance_id: str
    description: str
    resolution_ref: str | None = None

    @property
    def resolved(self) -> bool:
        return self.resolution_ref is not None


@dataclass(frozen=True)
class HandoverGate:
    ready: bool
    blockers: tuple[str, ...]


@dataclass
class AwardHandover:
    px_id: str
    award_ref: str
    contract_ref: str
    items: dict[str, HandoverItem] = field(default_factory=dict)
    variances: dict[str, ContractVariance] = field(default_factory=dict)
    activated: bool = False
    acceptance_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.px_id.strip() or not self.award_ref.strip() or not self.contract_ref.strip():
            raise ValueError("px_id, award_ref, and contract_ref must be non-empty")

    @property
    def project_id(self) -> str:
        return self.px_id

    @property
    def project_workspace(self) -> str:
        return f"OPS/Projects/{self.px_id}"

    def add_item(self, item_id: str, description: str, *, owner: str, required: bool) -> None:
        if item_id in self.items:
            raise ValueError(f"handover item {item_id} already exists")
        if not item_id.strip() or not description.strip() or not owner.strip():
            raise ValueError("item_id, description, and owner must be non-empty")
        self.items[item_id] = HandoverItem(item_id, description, owner, required)

    def complete_item(self, item_id: str, *, evidence_ref: str) -> None:
        if not evidence_ref.strip():
            raise ValueError("completed handover items require evidence_ref")
        current = self.items[item_id]
        self.items[item_id] = replace(
            current,
            status=HandoverItemStatus.COMPLETE,
            evidence_ref=evidence_ref,
        )

    def add_variance(self, variance_id: str, description: str) -> None:
        if variance_id in self.variances:
            raise ValueError(f"variance {variance_id} already exists")
        if not variance_id.strip() or not description.strip():
            raise ValueError("variance_id and description must be non-empty")
        self.variances[variance_id] = ContractVariance(variance_id, description)

    def resolve_variance(self, variance_id: str, *, resolution_ref: str) -> None:
        if not resolution_ref.strip():
            raise ValueError("resolved variances require resolution_ref")
        current = self.variances[variance_id]
        self.variances[variance_id] = replace(current, resolution_ref=resolution_ref)

    def readiness_gate(self, *, approved: bool) -> HandoverGate:
        blockers = [
            item_id
            for item_id, item in self.items.items()
            if item.required and item.status is not HandoverItemStatus.COMPLETE
        ]
        blockers.extend(
            variance_id
            for variance_id, variance in self.variances.items()
            if not variance.resolved
        )
        if not approved:
            blockers.append("ATLAS_APPROVAL")
        return HandoverGate(ready=not blockers, blockers=tuple(blockers))

    def activate_project(self, *, approved: bool, acceptance_ref: str) -> None:
        gate = self.readiness_gate(approved=approved)
        if not gate.ready:
            raise ValueError(f"handover is not ready: {', '.join(gate.blockers)}")
        if not acceptance_ref.strip():
            raise ValueError("project activation requires acceptance_ref")
        self.activated = True
        self.acceptance_ref = acceptance_ref


__all__ = [
    "AwardHandover",
    "ContractVariance",
    "HandoverGate",
    "HandoverItem",
    "HandoverItemStatus",
]
