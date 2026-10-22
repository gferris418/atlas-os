from __future__ import annotations

import hashlib
from collections.abc import Mapping

from .models import ExecutionEnvelope, ExecutionResult
from .quality import evaluate_quality_gate
from .router import PRE_EXECUTION_FLOW, choose_route, minimal_domain_framing, normalize_objective


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
    requested_quality_floor = envelope.context.get("required_quality_floor")
    framing = minimal_domain_framing(
        normalized,
        requested_quality_floor=requested_quality_floor if isinstance(requested_quality_floor, str) else None,
    )
    route = choose_route(normalized, envelope.approvals)

    approval_blocked = route.approval_required and route.approval_status != "APPROVED"
    state = "AWAITING_APPROVAL" if approval_blocked else "READY"
    active_stage = "APPROVAL" if approval_blocked else "EXECUTION"
    blocker = None
    next_action = f"Execute {route.mechanism} under ATLAS control."
    quality_gate_status = "NOT_EVALUATED"
    quality_gaps: list[str] = []
    evidence_health = "UNKNOWN"
    progress = 30 if approval_blocked else 50

    if approval_blocked:
        blocker = (
            "Explicit scoped approval is required before ARGUS activation."
            if route.mechanism in {"ARGUS", "MULTI_CAPABILITY"}
            else "Explicit scoped approval is required before the external action."
        )
        next_action = "Obtain explicit user approval or revise the route."

    trace = ("MISSION_CONTROL", *PRE_EXECUTION_FLOW)
    if envelope.provider_result is not None:
        trace = (*trace, "PROVIDER_RETURN_RECONCILIATION")
        next_action = (
            "ATLAS must reconcile the provider result, then choose CONTINUE, VERIFY, RETRY, "
            "REROUTE, REQUEST_APPROVAL, REQUEST_CLARIFICATION, COMPLETE, or FAIL."
        )

        ledger = envelope.provider_result.get("quality_ledger")
        if not approval_blocked and isinstance(ledger, Mapping):
            gate = evaluate_quality_gate(framing["required_quality_tier"], ledger)
            quality_gate_status = gate["status"]
            quality_gaps = list(gate["irreducible_gaps"])

            if quality_gate_status == "PASS":
                state = "READY_FOR_FINAL_VERIFY"
                active_stage = "FINAL_VERIFY"
                evidence_health = "SUFFICIENT"
                progress = 90
                next_action = "Run ATLAS final verification before persistence and delivery."
            elif quality_gate_status == "IRREDUCIBLE_GAP":
                state = "QUALITY_GAP_DISCLOSED"
                active_stage = "FINAL_VERIFY"
                evidence_health = "GAPS_DISCLOSED"
                progress = 90
                blocker = "; ".join(gate["blocking_reasons"]) or None
                next_action = "Run ATLAS final verification with explicit disclosure of irreducible gaps."
            else:
                state = "QUALITY_GATE_BLOCKED"
                active_stage = "QUALITY_GATE"
                evidence_health = "INSUFFICIENT"
                progress = 80
                blocker = "; ".join(gate["blocking_reasons"]) or None
                next_action = "Continue targeted collection or analysis until the required quality tier is satisfied."

    dashboard = {
        "system": "ATLAS",
        "host": envelope.host,
        "task_id": task_id,
        "objective": normalized,
        "progress": progress,
        "active_stage": active_stage,
        "blocker_or_approval": blocker,
        "evidence_health": evidence_health,
        "quality_tier": framing["required_quality_tier"],
        "quality_gate": quality_gate_status,
        "quality_gaps": quality_gaps,
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
