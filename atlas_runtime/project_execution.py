from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum


class MilestoneStatus(str, Enum):
    OPEN = "OPEN"
    ACCEPTED = "ACCEPTED"


@dataclass(frozen=True)
class ProjectMilestone:
    milestone_id: str
    description: str
    owner: str
    due_date: str
    contract_obligation_ref: str
    required: bool = True
    payment_trigger: bool = False
    dependencies: tuple[str, ...] = ()
    status: MilestoneStatus = MilestoneStatus.OPEN
    evidence_ref: str | None = None


@dataclass(frozen=True)
class ProjectIssue:
    issue_id: str
    description: str
    owner: str
    milestone_id: str | None = None
    resolution_ref: str | None = None

    @property
    def resolved(self) -> bool:
        return self.resolution_ref is not None


@dataclass(frozen=True)
class CompletionGate:
    ready: bool
    blockers: tuple[str, ...]


@dataclass
class ProjectExecution:
    px_id: str
    contract_ref: str
    milestones: dict[str, ProjectMilestone] = field(default_factory=dict)
    issues: dict[str, ProjectIssue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.px_id.strip() or not self.contract_ref.strip():
            raise ValueError("px_id and contract_ref must be non-empty")

    def add_milestone(
        self,
        milestone_id: str,
        description: str,
        *,
        owner: str,
        due_date: str,
        contract_obligation_ref: str,
        required: bool = True,
        payment_trigger: bool = False,
        dependencies: list[str] | None = None,
    ) -> None:
        if milestone_id in self.milestones:
            raise ValueError(f"milestone {milestone_id} already exists")
        if not all(value.strip() for value in (milestone_id, description, owner, due_date, contract_obligation_ref)):
            raise ValueError("milestone fields must be non-empty")
        dependency_ids = tuple(dependencies or ())
        unknown = [item for item in dependency_ids if item not in self.milestones]
        if unknown:
            raise ValueError(f"unknown milestone dependencies: {', '.join(unknown)}")
        self.milestones[milestone_id] = ProjectMilestone(
            milestone_id,
            description,
            owner,
            due_date,
            contract_obligation_ref,
            required,
            payment_trigger,
            dependency_ids,
        )

    def add_issue(self, issue_id: str, description: str, *, owner: str, milestone_id: str | None = None) -> None:
        if issue_id in self.issues:
            raise ValueError(f"issue {issue_id} already exists")
        if not issue_id.strip() or not description.strip() or not owner.strip():
            raise ValueError("issue_id, description, and owner must be non-empty")
        if milestone_id is not None and milestone_id not in self.milestones:
            raise ValueError(f"unknown milestone {milestone_id}")
        self.issues[issue_id] = ProjectIssue(issue_id, description, owner, milestone_id)

    def resolve_issue(self, issue_id: str, *, resolution_ref: str) -> None:
        if not resolution_ref.strip():
            raise ValueError("resolved issues require resolution_ref")
        self.issues[issue_id] = replace(self.issues[issue_id], resolution_ref=resolution_ref)

    def accept_milestone(self, milestone_id: str, *, evidence_ref: str) -> None:
        if not evidence_ref.strip():
            raise ValueError("accepted milestones require evidence_ref")
        milestone = self.milestones[milestone_id]
        incomplete_dependencies = [
            dependency_id
            for dependency_id in milestone.dependencies
            if self.milestones[dependency_id].status is not MilestoneStatus.ACCEPTED
        ]
        if incomplete_dependencies:
            raise ValueError(f"incomplete dependencies: {', '.join(incomplete_dependencies)}")
        open_issues = [
            issue_id
            for issue_id, issue in self.issues.items()
            if issue.milestone_id == milestone_id and not issue.resolved
        ]
        if open_issues:
            raise ValueError(f"open milestone issues: {', '.join(open_issues)}")
        self.milestones[milestone_id] = replace(
            milestone,
            status=MilestoneStatus.ACCEPTED,
            evidence_ref=evidence_ref,
        )

    def payment_ready_milestones(self) -> tuple[str, ...]:
        return tuple(
            milestone_id
            for milestone_id, milestone in self.milestones.items()
            if milestone.payment_trigger
            and milestone.status is MilestoneStatus.ACCEPTED
            and milestone.evidence_ref is not None
        )

    def completion_gate(self) -> CompletionGate:
        blockers = [
            milestone_id
            for milestone_id, milestone in self.milestones.items()
            if milestone.required and milestone.status is not MilestoneStatus.ACCEPTED
        ]
        blockers.extend(
            issue_id
            for issue_id, issue in self.issues.items()
            if not issue.resolved
        )
        return CompletionGate(ready=not blockers, blockers=tuple(blockers))


__all__ = [
    "CompletionGate",
    "MilestoneStatus",
    "ProjectExecution",
    "ProjectIssue",
    "ProjectMilestone",
]
