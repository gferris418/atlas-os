from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionEnvelope:
    objective: str
    task_id: str | None = None
    host: str = "generic-host"
    context: Mapping[str, Any] = field(default_factory=dict)
    approvals: tuple[str, ...] = ()
    provider_result: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")
        if self.task_id is not None and (
            not isinstance(self.task_id, str) or not self.task_id.strip()
        ):
            raise ValueError("task_id must be a non-empty string or null")
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host must be a non-empty string")
        if not isinstance(self.context, Mapping):
            raise ValueError("context must be a mapping")
        if not isinstance(self.approvals, tuple) or any(
            not isinstance(approval, str) or not approval.strip()
            for approval in self.approvals
        ):
            raise ValueError("approvals must be a tuple of non-empty strings")
        if self.provider_result is not None and not isinstance(self.provider_result, Mapping):
            raise ValueError("provider_result must be a mapping or null")
        object.__setattr__(self, "context", deepcopy(dict(self.context)))
        if self.provider_result is not None:
            object.__setattr__(self, "provider_result", deepcopy(dict(self.provider_result)))
        object.__setattr__(self, "approvals", tuple(dict.fromkeys(self.approvals)))


@dataclass(frozen=True)
class RouteDecision:
    mechanism: str
    capability: str
    provider: str | None
    approval_required: bool
    approval_status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mechanism": self.mechanism,
            "capability": self.capability,
            "provider": self.provider,
            "approval_required": self.approval_required,
            "approval_status": self.approval_status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ExecutionResult:
    task_id: str
    state: str
    original_input: str
    normalized_objective: str
    domain_framing: Mapping[str, Any]
    pre_execution_flow: tuple[str, ...]
    route: RouteDecision
    next_step_authority: str
    provider_return_target: str
    execution_trace: tuple[str, ...]
    dashboard: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "state": self.state,
            "original_input": self.original_input,
            "normalized_objective": self.normalized_objective,
            "domain_framing": dict(self.domain_framing),
            "pre_execution_flow": list(self.pre_execution_flow),
            "route": self.route.to_dict(),
            "next_step_authority": self.next_step_authority,
            "provider_return_target": self.provider_return_target,
            "execution_trace": list(self.execution_trace),
            "dashboard": dict(self.dashboard),
        }
