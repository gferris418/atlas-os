from __future__ import annotations

import hashlib

from .contract import PRE_EXECUTION_FLOW
from .models import ExecutionEnvelope, ExecutionResult
from .router import choose_route, minimal_domain_framing, normalize_objective


def enter_mission_control(envelope: ExecutionEnvelope) -> str:
    """Enter the ATLAS governance gate and return the raw objective for preprocessing."""
    return envelope.objective


def _task_id(envelope: ExecutionEnvelope, normalized: str) -> str:
    if envelope.task_id:
        return envelope.task_id
    digest = hashlib.sha256((envelope.host + "\0" + normalized).encode("utf-8")).hexdigest()[:12].upper()
    return f"ATLAS-{digest}"


def execute(envelope: ExecutionEnvelope) -> ExecutionResult:
    original = enter_mission_control(envelope)
    normalized = normalize_objective(original)
    task_id = _task_id(envelope, normalized)
    framing = minimal_domain_framing(normalized)
    route = choose_route(normalized, envelope.approvals)

    approval_blocked = route.approval_required and route.approval_status != "APPROVED"
    state = "AWAITING_APPROVAL" if approval_blocked else "READY"
    active_stage = "APPROVAL" if approval_blocked else "EXECUTION"
    blocker = None
    next_action = f"Execute {route.mechanism} under ATLAS control."
    if approval_blocked:
        blocker = (
            "Explicit scoped approval is required before ARGUS activation."
            if route.mechanism in {"ARGUS", "MULTI_CAPABILITY"}
            else "Explicit scoped approval is required before the external action."
        )
        next_action = "Obtain explicit user approval or revise the route."

    trace: tuple[str, ...] = ("MISSION_CONTROL", *PRE_EXECUTION_FLOW)
    if envelope.provider_result is not None:
        trace = (*trace, "PROVIDER_RETURN_RECONCILIATION")
        next_action = (
            "ATLAS must reconcile the provider result, then choose CONTINUE, VERIFY, RETRY, "
            "REROUTE, REQUEST_APPROVAL, REQUEST_CLARIFICATION, COMPLETE, or FAIL."
        )

    progress = 30 if approval_blocked else 50
    dashboard = {
        "system": "ATLAS",
        "host": envelope.host,
        "task_id": task_id,
        "objective": normalized,
        "progress": progress,
        "active_stage": active_stage,
        "blocker_or_approval": blocker,
        "evidence_health": "UNKNOWN",
        "persistence_state": "NOT_REQUIRED",
        "next_action": next_action,
        "route": route.mechanism,
        "next_step_authority": "ATLAS",
    }

    return ExecutionResult(
        task_id=task_id,
        state=state,
        original_input=original,
        normalized_objective=normalized,
        domain_framing=framing,
        pre_execution_flow=PRE_EXECUTION_FLOW,
        route=route,
        next_step_authority="ATLAS",
        provider_return_target="ATLAS",
        execution_trace=trace,
        dashboard=dashboard,
    )
