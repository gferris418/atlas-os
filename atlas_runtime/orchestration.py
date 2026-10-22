"""Portable ATLAS orchestration seam over the stable reference runtime.

This module keeps the existing execution engine as the implementation core while
making user authorization for ARGUS an explicit, digest-bound Control Plane state.
Hosts should enter ATLAS through this module (or the package-level exports) rather
than calling the lower-level engine directly.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any

from .engine import (
    ExecutionEnvelope as _EngineExecutionEnvelope,
    ExecutionResult,
    execute as _engine_execute,
)
from .routing import build_routing_preview as _base_build_routing_preview
from .runtime import classify_task, normalize_intent
from .triage import triage_request

_ARGUS_COLLECTION_MODES = {"ARGUS_COLLECTION", "HYBRID"}
_APPROVAL_STATES = {"PENDING", "APPROVED", "REJECTED"}


@dataclass(frozen=True)
class ExecutionEnvelope(_EngineExecutionEnvelope):
    """Host-neutral ATLAS envelope with explicit digest-bound ARGUS authorization."""

    argus_approval_status: str = "PENDING"
    argus_approval_digest: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.argus_approval_status not in _APPROVAL_STATES:
            raise ValueError("invalid ARGUS approval status")
        if self.argus_approval_digest is not None and not isinstance(self.argus_approval_digest, str):
            raise TypeError("argus_approval_digest must be a string or null")


def _requires_argus(objective: str) -> bool:
    normalized = normalize_intent(objective)["normalized"]
    task_classes = tuple(classify_task(normalized))
    triage = triage_request(normalized, task_classes=task_classes)
    return triage["collection_mode"] in _ARGUS_COLLECTION_MODES


def _effective_authorization_status(
    *,
    argus_required: bool,
    requested_status: str,
    approval_digest: str | None,
    current_digest: str | None,
) -> str:
    if not argus_required:
        return "NOT_REQUIRED"
    if requested_status == "APPROVED" and approval_digest != current_digest:
        return "STALE"
    return requested_status


def _upgrade_activation_contract(
    preview: dict[str, Any],
    *,
    argus_approval_status: str,
    argus_approval_digest: str | None = None,
    activation_observed: bool = False,
) -> dict[str, Any]:
    """Project activation-contract v2 without changing the proposal digest.

    The digest binds the proposed route, mission, providers, permissions and
    handoff requirements. Authorization state is outside that proposal digest and
    independently records which digest Mission Control approved.
    """

    upgraded = deepcopy(preview)
    legacy = deepcopy(upgraded["activation_contract"])
    collection_mode = legacy.get("collection_mode", "NONE")
    argus_required = collection_mode in _ARGUS_COLLECTION_MODES
    current_digest = upgraded.get("digest")
    authorization_status = _effective_authorization_status(
        argus_required=argus_required,
        requested_status=argus_approval_status,
        approval_digest=argus_approval_digest,
        current_digest=current_digest,
    )

    structural_blockers = list(legacy.get("blockers", []))
    blockers = list(structural_blockers)
    if argus_required and authorization_status == "PENDING":
        blockers.append("ARGUS_EXPLICIT_APPROVAL_REQUIRED")
    elif argus_required and authorization_status == "REJECTED":
        blockers.append("ARGUS_EXPLICIT_APPROVAL_REJECTED")
    elif argus_required and authorization_status == "STALE":
        blockers.append("ARGUS_APPROVAL_DIGEST_MISMATCH")
    blockers = list(dict.fromkeys(blockers))

    if not argus_required:
        activation_status = "NOT_REQUIRED"
    elif authorization_status != "APPROVED":
        activation_status = "NOT_AUTHORIZED"
    elif structural_blockers:
        activation_status = "AUTHORIZED_BUT_BLOCKED"
    elif activation_observed:
        activation_status = "AUTHORIZED"
    else:
        activation_status = "AUTHORIZED"

    state = legacy.get("state", "NOT_REQUIRED")
    if argus_required and authorization_status == "REJECTED":
        state = "BLOCKED"
    elif argus_required and authorization_status in {"PENDING", "STALE"} and state != "BLOCKED":
        state = "READY_FOR_APPROVAL"

    task_id = upgraded.get("task_id")
    mission_id = legacy.get("collection_mission_id")
    upgraded["activation_contract"] = {
        **legacy,
        "version": "2.0",
        "state": state,
        "blockers": blockers,
        "route": {
            "collection_mode": collection_mode,
            "routing_preview_digest": current_digest,
        },
        "argus": {
            "required": argus_required,
            "authorization": {
                "required": argus_required,
                "status": authorization_status,
                "scope_task_id": task_id if argus_required else None,
                "bound_preview_digest": argus_approval_digest if argus_required else None,
                "reusable": False,
                "decision_source": (
                    "MISSION_CONTROL"
                    if argus_required and argus_approval_status in {"APPROVED", "REJECTED"}
                    else None
                ),
            },
            "activation": {
                "status": activation_status,
            },
            "mission": {
                "id": mission_id,
            },
        },
    }
    return upgraded


def build_routing_preview(
    *args: Any,
    argus_approval_status: str = "PENDING",
    argus_approval_digest: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build the canonical proposal plus the portable activation-contract v2 projection."""

    if argus_approval_status not in _APPROVAL_STATES:
        raise ValueError("invalid ARGUS approval status")
    preview = _base_build_routing_preview(*args, **kwargs)
    return _upgrade_activation_contract(
        preview,
        argus_approval_status=argus_approval_status,
        argus_approval_digest=argus_approval_digest,
    )


def execute(envelope: ExecutionEnvelope) -> ExecutionResult:
    """Run ATLAS while enforcing explicit permission before any ARGUS handoff.

    `collection_mode` answers whether ARGUS is required. The authorization fields
    answer whether Mission Control explicitly approved the current routing digest.
    These states are intentionally independent.
    """

    argus_required = _requires_argus(envelope.objective)
    approval_is_candidate_current = (
        envelope.argus_approval_status == "APPROVED"
        and envelope.argus_approval_digest is not None
        and envelope.argus_approval_digest == envelope.routing_preview_digest
    )

    # The lower-level engine already fails closed at routing approval. Reuse that
    # gate so ARGUS is never routed unless the host presents an explicit ARGUS
    # approval bound to the same digest being offered for routing approval.
    effective_envelope: _EngineExecutionEnvelope = envelope
    if argus_required and not approval_is_candidate_current:
        effective_envelope = replace(envelope, routing_approval_status="PENDING")

    base_result = _engine_execute(effective_envelope)
    activation_observed = any(
        decision.get("provider_id") == "domain-method.argus-intelligence"
        and decision.get("status") == "ROUTED"
        for decision in base_result.routing_decisions
    )
    routing_preview = _upgrade_activation_contract(
        base_result.routing_preview,
        argus_approval_status=envelope.argus_approval_status,
        argus_approval_digest=envelope.argus_approval_digest,
        activation_observed=activation_observed,
    )

    # Keep the lower-level dashboard's schema-compatible routing preview intact.
    # Portable hosts consume result.routing_preview for activation-contract v2 and
    # the dashboard's active-stage/blocker fields for visible authorization state.
    dashboard = deepcopy(base_result.dashboard)
    state = base_result.state
    active_unit = base_result.active_unit
    routing_decisions = base_result.routing_decisions

    contract = routing_preview["activation_contract"]
    authorization_status = contract["argus"]["authorization"]["status"]
    structural_blockers = [
        blocker
        for blocker in contract["blockers"]
        if not blocker.startswith("ARGUS_EXPLICIT_APPROVAL_")
        and blocker != "ARGUS_APPROVAL_DIGEST_MISMATCH"
    ]
    earlier_control_blocker = dashboard.get("active_stage") == "MATERIAL_CONTEXT_MATRIX"

    if argus_required and not structural_blockers and not earlier_control_blocker:
        if authorization_status in {"PENDING", "STALE"}:
            state = "AWAITING_APPROVAL"
            active_unit = None
            routing_decisions = ()
            dashboard["plan_status"] = "BLOCKED"
            dashboard["active_stage"] = "ARGUS_APPROVAL"
            dashboard["active_unit"] = (
                "Renew ARGUS authorization for the current routing preview"
                if authorization_status == "STALE"
                else "Approve or reject ARGUS collection"
            )
            dashboard["blocker_or_approval"] = (
                "ARGUS authorization is stale because the approved digest does not match the current routing preview."
                if authorization_status == "STALE"
                else "Explicit user approval is required before ARGUS handoff or activation."
            )
            dashboard["pending_decision"] = "Approve or reject ARGUS collection for this exact task and routing preview."
            dashboard["next_action"] = "Record explicit Mission Control authorization bound to the current routing preview digest."
            dashboard["quality_gate"] = "BLOCKED"
        elif authorization_status == "REJECTED":
            state = "BLOCKED"
            active_unit = None
            routing_decisions = ()
            dashboard["plan_status"] = "BLOCKED"
            dashboard["active_stage"] = "ARGUS_APPROVAL"
            dashboard["active_unit"] = "ARGUS authorization rejected"
            dashboard["blocker_or_approval"] = (
                "ARGUS authorization was rejected; revise the route or continue only with work that does not require ARGUS."
            )
            dashboard["pending_decision"] = "Revise the collection route or task scope."
            dashboard["next_action"] = "Return to Route without activating ARGUS."
            dashboard["quality_gate"] = "BLOCKED"

    return replace(
        base_result,
        state=state,
        active_unit=active_unit,
        dashboard=dashboard,
        routing_preview=routing_preview,
        routing_decisions=tuple(routing_decisions),
    )


__all__ = ["ExecutionEnvelope", "ExecutionResult", "build_routing_preview", "execute"]
