"""ATLAS-owned construction and validation of bounded ARGUS collection missions."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
_COLLECTION_MISSION_SCHEMA = json.loads(
    (ROOT / "schemas/collection-mission.schema.json").read_text(encoding="utf-8")
)
_COLLECTION_MISSION_VALIDATOR = jsonschema.Draft202012Validator(
    _COLLECTION_MISSION_SCHEMA,
    format_checker=jsonschema.FormatChecker(),
)

_STARTUP_SEQUENCE = [
    "RESOLVE_INSTITUTIONAL_HIERARCHY",
    "CHECK_INTERNAL_CANONICAL_REGISTRY",
    "RECONCILE_OPPORTUNITY_IDENTITY",
    "CHECK_OFFICIAL_PROCUREMENT_SOURCES",
    "CHECK_INTERNAL_CUSTOMER_INTELLIGENCE",
    "BUILD_RESEARCH_FRONTIER",
    "EXECUTE_ADAPTIVE_360_COLLECTION",
]

_ESCALATION_CONDITIONS = [
    "MATERIAL_SCOPE_CHANGE",
    "AUTHORIZATION_REQUIRED",
    "POLICY_OR_SECURITY_CONFLICT",
    "MATERIAL_AMBIGUITY",
]


def validate_collection_mission(
    mission: Mapping[str, Any],
    *,
    task_id: str | None = None,
    plan_id: str | None = None,
    allowed_modes: set[str] | None = None,
) -> dict[str, Any]:
    """Validate a collection mission and optionally bind it to current execution identity."""

    record = deepcopy(dict(mission))
    try:
        _COLLECTION_MISSION_VALIDATOR.validate(record)
    except jsonschema.ValidationError as error:
        raise ValueError(f"invalid collection mission: {error.message}") from error
    if task_id is not None and record["source_task_id"] != task_id:
        raise ValueError("collection mission source_task_id does not match current task")
    if plan_id is not None and record["source_plan_id"] != plan_id:
        raise ValueError("collection mission source_plan_id does not match current plan")
    if allowed_modes is not None and record["collection_mode"] not in allowed_modes:
        raise ValueError("collection mission mode is not authorized for this activation")
    return record


def _temporal_scope(objective: str) -> tuple[str | None, str]:
    normalized = " ".join(objective.split())
    explicit_years = re.findall(r"\b(?:19|20)\d{2}\b", normalized)
    if explicit_years:
        unique_years = list(dict.fromkeys(explicit_years))
        horizon = unique_years[0] if len(unique_years) == 1 else f"{unique_years[0]}-{unique_years[-1]}"
        return horizon, "HISTORICAL"

    horizon_match = re.search(
        r"\b(?:over|within|next)\s+(\d+\s+(?:day|week|month|year)s?)\b",
        normalized,
        re.IGNORECASE,
    )
    if horizon_match:
        return horizon_match.group(1), "CURRENT"

    if re.search(r"\b(?:historical|archive|archived|previous|past)\b", normalized, re.IGNORECASE):
        return None, "HISTORICAL"
    if re.search(r"\b(?:latest|current|today|present)\b", normalized, re.IGNORECASE):
        return None, "CURRENT"
    return None, "CURRENT"


def _execution_policy() -> dict[str, Any]:
    """Return the fixed bounded-autonomy policy for one ATLAS-delegated ARGUS mission."""

    return {
        "handoff_pattern": "ONE_HANDOFF_ONE_RETURN",
        "autonomy_mode": "BOUNDED_AUTONOMOUS",
        "startup_sequence": list(_STARTUP_SEQUENCE),
        "identity_resolution": {
            "auto_reuse": ["EXACT", "HIGH_CONFIDENCE_MATCH"],
            "auto_new_candidate": ["DISTINCT"],
            "escalate": ["PROBABLE_MATCH", "UNRESOLVED"],
        },
        "identity_confirmation": "AMBIGUOUS_ONLY",
        "escalation_conditions": list(_ESCALATION_CONDITIONS),
        "follow_evidence_leads_without_callback": True,
        "parallel_safe_reads": True,
        "persistence_mode": "PROPOSE_BATCH_THEN_ATLAS_COMMIT",
        "mission_context": "TRANSIENT_ONLY",
    }


def build_collection_mission(
    objective: str,
    *,
    task_id: str,
    plan_id: str,
    request_triage: Mapping[str, Any],
    risk_flags: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    """Build the minimum bounded mission needed for an ARGUS collection activation."""

    mode = str(request_triage.get("collection_mode", ""))
    if mode not in {"ARGUS_COLLECTION", "HYBRID"}:
        raise ValueError("collection mission requires an ARGUS activating collection mode")
    collection_types = list(dict.fromkeys(request_triage.get("collection_types", [])))
    if not collection_types:
        raise ValueError("collection mission requires at least one collection type")
    depth = request_triage.get("collection_depth")
    if not depth:
        raise ValueError("collection mission requires a collection depth")

    normalized = " ".join(objective.split())
    jurisdictions: list[str] = []
    if re.search(r"\bbangladesh\b", normalized, re.IGNORECASE):
        jurisdictions.append("Bangladesh")
    if re.search(r"\bsingapore\b", normalized, re.IGNORECASE):
        jurisdictions.append("Singapore")
    time_horizon, freshness_requirement = _temporal_scope(normalized)

    mission = {
        "mission_id": "COLLECTION-" + task_id.removeprefix("TASK-"),
        "source_task_id": task_id,
        "source_plan_id": plan_id,
        "objective": normalized,
        "collection_mode": mode,
        "collection_types": collection_types,
        "targets": [{"name": normalized, "target_type": None, "aliases": []}],
        "collection_questions": [
            f"Collect and corroborate evidence required for {collection_type.lower().replace('_', ' ')}."
            for collection_type in collection_types
        ],
        "jurisdictions": jurisdictions,
        "time_horizon": time_horizon,
        "freshness_requirement": freshness_requirement,
        "collection_depth": depth,
        "source_priorities": ["official", "primary", "authoritative-secondary"],
        "source_exclusions": [],
        "risk_flags": list(dict.fromkeys(risk_flags)),
        "required_output_components": ["findings", "evidence", "collection_gaps", "unknowns_conflicts"],
        "execution_policy": _execution_policy(),
        "stopping_rule": (
            "Stop when the requested collection questions are materially answered with corroborated evidence, "
            "or when remaining gaps are explicit and further collection is unlikely to change the commercial decision, "
            "identity outcome, lifecycle interpretation, supplier strategy, or next authorized ATLAS action."
        ),
    }
    return validate_collection_mission(
        mission,
        task_id=task_id,
        plan_id=plan_id,
        allowed_modes={"ARGUS_COLLECTION", "HYBRID"},
    )


__all__ = ["build_collection_mission", "validate_collection_mission"]
