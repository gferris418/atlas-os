from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum


class RequirementStatus(str, Enum):
    OPEN = "OPEN"
    SATISFIED = "SATISFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class BidRequirement:
    requirement_id: str
    text: str
    mandatory: bool
    owner: str
    status: RequirementStatus = RequirementStatus.OPEN
    evidence_ref: str | None = None
    addenda: tuple[str, ...] = ()


@dataclass(frozen=True)
class SubmissionGate:
    ready: bool
    blockers: tuple[str, ...]


@dataclass
class BidWorkspace:
    px_id: str
    deadline: str
    requirements: dict[str, BidRequirement] = field(default_factory=dict)
    submission_channel: str | None = None
    submission_receipt_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.px_id.strip():
            raise ValueError("px_id must be non-empty")
        if not self.deadline.strip():
            raise ValueError("deadline must be non-empty")

    def add_requirement(self, requirement_id: str, text: str, *, mandatory: bool, owner: str) -> None:
        if requirement_id in self.requirements:
            raise ValueError(f"requirement {requirement_id} already exists")
        if not requirement_id.strip() or not text.strip() or not owner.strip():
            raise ValueError("requirement_id, text, and owner must be non-empty")
        self.requirements[requirement_id] = BidRequirement(requirement_id, text, mandatory, owner)

    def update_requirement(
        self,
        requirement_id: str,
        *,
        status: RequirementStatus,
        evidence_ref: str | None = None,
    ) -> None:
        current = self.requirements[requirement_id]
        if status is RequirementStatus.SATISFIED and not evidence_ref:
            raise ValueError("satisfied requirements require evidence_ref")
        self.requirements[requirement_id] = replace(current, status=status, evidence_ref=evidence_ref)

    def apply_addendum(self, addendum_id: str, *, affected_requirement_ids: list[str]) -> None:
        if not addendum_id.strip():
            raise ValueError("addendum_id must be non-empty")
        for requirement_id in affected_requirement_ids:
            current = self.requirements[requirement_id]
            addenda = tuple(dict.fromkeys((*current.addenda, addendum_id)))
            self.requirements[requirement_id] = replace(
                current,
                status=RequirementStatus.REVIEW_REQUIRED,
                addenda=addenda,
            )

    def submission_gate(self, *, approved: bool) -> SubmissionGate:
        blockers = [
            requirement_id
            for requirement_id, requirement in self.requirements.items()
            if requirement.mandatory and requirement.status is not RequirementStatus.SATISFIED
        ]
        if not approved:
            blockers.append("ATLAS_APPROVAL")
        return SubmissionGate(ready=not blockers, blockers=tuple(blockers))

    def record_submission(self, channel: str, *, receipt_ref: str) -> None:
        if not channel.strip() or not receipt_ref.strip():
            raise ValueError("submission channel and receipt_ref must be non-empty")
        self.submission_channel = channel
        self.submission_receipt_ref = receipt_ref


__all__ = ["BidRequirement", "BidWorkspace", "RequirementStatus", "SubmissionGate"]
