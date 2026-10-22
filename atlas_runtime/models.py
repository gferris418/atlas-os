from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


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
        if not isinstance(self.host, str) or not self.host.strip():
            raise ValueError("host must be a non-empty string")
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
