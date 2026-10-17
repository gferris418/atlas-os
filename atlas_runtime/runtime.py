"""Small executable reference for the normative ATLAS contracts.

The declarative specifications remain authoritative. This module exists so the
core invariants can be exercised at stable public seams.
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Iterable
from zoneinfo import ZoneInfo


TASK_CLASSES = {
    "ANSWER", "RESEARCH", "ANALYSIS", "DECISION", "WRITING", "DOCUMENT",
    "DATA", "CODING", "DEBUGGING", "DESIGN", "PLANNING", "WORKFLOW",
    "EXTERNAL_ACTION", "MONITORING", "MULTI_STAGE",
}

HIGH_IMPACT_ACTIONS = {
    "delete", "publish", "pay", "purchase", "send_external",
    "change_permissions", "rotate_credentials", "release",
}

EVIDENCE_CLASSES = {
    "VERIFIED", "SUPPORTED", "INFERRED", "ASSUMED", "SPECULATIVE", "UNKNOWN",
}

FRAMEWORK_AUTHORITIES = {
    "international-standard",
    "professional-framework",
    "official-primary",
}

RELEASE_TRANSITIONS = {
    "DRAFT": {"CANDIDATE"},
    "CANDIDATE": {"VERIFIED"},
    "VERIFIED": {"RELEASED"},
    "RELEASED": {"SUPERSEDED"},
    "SUPERSEDED": {"ARCHIVED"},
    "ARCHIVED": set(),
}

_CRITICAL_LITERAL = re.compile(
    r"(?:\b\d+(?:\.\d+)?(?:%|[A-Za-z]+)?\b|"
    r"\b\d{4}-\d{2}-\d{2}\b|"
    r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+\b|"
    r"`[^`]+`|\"[^\"]+\"|'[^']+')"
)


class ApprovalRequired(PermissionError):
    """Raised when an action crosses an unapproved authority boundary."""


class CanonicalRevisionInUse(RuntimeError):
    """Raised when an active dependency protects a canonical revision."""


@dataclass(frozen=True)
class PersistenceReceipt:
    """Validated evidence emitted after a durable adapter verifies its write."""

    adapter: str
    location: str
    checksum: str
    bytes_written: int
    verified_at: str

    def __post_init__(self) -> None:
        if not self.adapter or not self.location:
            raise ValueError("persistence receipt requires adapter and location")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", self.checksum):
            raise ValueError("persistence receipt requires a SHA-256 checksum")
        if self.bytes_written < 0:
            raise ValueError("persistence receipt bytes_written cannot be negative")
        try:
            moment = datetime.fromisoformat(self.verified_at)
        except ValueError as error:
            raise ValueError("persistence receipt verified_at must be RFC 3339") from error
        if moment.tzinfo is None:
            raise ValueError("persistence receipt verified_at requires an offset")


def normalize_intent(text: str) -> dict[str, Any]:
    """Normalize whitespace without losing critical literal values."""
    original = text
    literals = _CRITICAL_LITERAL.findall(original)
    normalized = " ".join(original.split())
    missing = [literal for literal in literals if literal not in normalized]
    if missing:
        raise ValueError(f"normalization lost critical literals: {missing}")
    return {"original": original, "normalized": normalized, "critical_literals": literals}


def assess_completeness(task: dict[str, Any]) -> dict[str, Any]:
    """Deterministic fallback for material gaps when host understanding is unavailable."""
    dimensions = ("who", "what", "when", "where", "why", "which", "how", "how_much")
    material = set(task.get("material_dimensions", ("what", "how")))
    supplied = {name for name in dimensions if task.get(name) not in (None, "", [])}
    missing_material = sorted(material - supplied)
    assumptions = deepcopy(task.get("assumptions", []))
    questions = []
    for name in missing_material:
        if name in task.get("safe_assumptions", {}):
            assumptions.append({"dimension": name, "value": task["safe_assumptions"][name]})
        else:
            questions.append(name)
    return {
        "assessed": list(dimensions),
        "supplied": sorted(supplied),
        "missing_material": missing_material,
        "questions": questions,
        "assumptions": assumptions,
        "complete": not questions,
    }


def classify_task(text: str) -> list[str]:
    """Return fallback task labels; capable host classification takes precedence."""
    lowered = text.lower()
    labels: set[str] = set()
    rules = {
        "CODING": ("code", "implement", "repository", "bug", "test"),
        "DEBUGGING": ("debug", "failure", "broken", "error"),
        "RESEARCH": ("research", "find", "sources"),
        "ANALYSIS": ("analyze", "compare", "assess"),
        "WRITING": ("write", "draft", "rewrite"),
        "DOCUMENT": ("document", "report", "proposal"),
        "DATA": ("dataset", "spreadsheet", "metrics"),
        "DESIGN": ("design", "architecture", "schema"),
        "PLANNING": ("plan", "roadmap", "schedule"),
        "WORKFLOW": ("workflow", "pipeline", "process"),
        "EXTERNAL_ACTION": ("send", "publish", "upload", "purchase"),
        "MONITORING": ("monitor", "watch", "alert"),
        "DECISION": ("decide", "recommend", "choose"),
    }
    for label, tokens in rules.items():
        if any(token in lowered for token in tokens):
            labels.add(label)
    if not labels:
        labels.add("ANSWER")
    if len(labels) > 2 or any(token in lowered for token in ("multi-stage", "end-to-end", "then")):
        labels.add("MULTI_STAGE")
    return sorted(labels & TASK_CLASSES)


def classify_domain_context(
    text: str,
    classifications: Iterable[dict[str, Any]],
    *,
    substantive: bool = True,
    required_facets: Iterable[str] | None = None,
    active_conditions: Iterable[str] = (),
) -> dict[str, Any]:
    """Classify domain context without guessing missing taxonomy codes.

    This lexical matcher is a deterministic fallback. Capable hosts should
    identify candidates natively, then use the governed records and explicit
    material facets for validation. Records may use ``triggers`` for any-term
    matching and ``match_all`` for phrase-component matching. Conditional
    records remain candidates until their declared context is active.
    """
    if not substantive:
        return {
            "status": "NOT_REQUIRED",
            "facets": {},
            "taxonomy_references": [],
            "risk_flags": [],
            "unresolved_facets": [],
            "conditional_candidates": [],
            "evidence": [],
            "next_action": None,
        }

    lowered = " ".join(text.lower().split())
    enabled_conditions = set(active_conditions)
    facets: dict[str, list[dict[str, str]]] = defaultdict(list)
    taxonomy_references: set[str] = set()
    risk_flags: set[str] = set()
    conditional_candidates: list[dict[str, Any]] = []

    for record in classifications:
        if record.get("status") != "active":
            continue
        triggers = [str(term).lower() for term in record.get("triggers", [])]
        match_all = [str(term).lower() for term in record.get("match_all", [])]
        lexical_match = (
            (bool(triggers) and any(term in lowered for term in triggers))
            or (bool(match_all) and all(term in lowered for term in match_all))
        )
        if not lexical_match:
            continue

        conditions = set(record.get("conditions", []))
        if not conditions.issubset(enabled_conditions):
            conditional_candidates.append({
                "id": record["id"],
                "taxonomy": record["taxonomy"],
                "code": record["code"],
                "label": record["label"],
                "version": record.get("version", "current-official"),
                "source": record.get("source"),
                "conditions": sorted(conditions),
            })
            continue

        facet = record["facet"]
        facets[facet].append({
            "id": record["id"],
            "taxonomy": record["taxonomy"],
            "code": record["code"],
            "label": record["label"],
            "version": record.get("version", "current-official"),
            "source": record.get("source"),
        })
        taxonomy_references.add(record["taxonomy"])
        risk_flags.update(record.get("risk_flags", []))

    ordered_facets = {
        facet: sorted(values, key=lambda item: item["id"])
        for facet, values in sorted(facets.items())
    }
    material_policy_known = required_facets is not None
    unresolved = sorted(set(required_facets or ()) - set(ordered_facets))
    conditional_candidates.sort(key=lambda item: item["id"])

    if not ordered_facets:
        status = "RESEARCH_REQUIRED"
        next_action = "Identify current authoritative taxonomy and classification sources for this domain."
    elif not material_policy_known:
        status = "PARTIAL"
        next_action = "Determine which classification facets are material before declaring classification complete."
    elif unresolved:
        status = "PARTIAL"
        if {"defense", "national-security", "operational-security"} & risk_flags:
            next_action = (
                "Clarify the unresolved facets, intended lifecycle, authorization, and permitted "
                "information sensitivity before selecting domain frameworks."
            )
        else:
            next_action = "Clarify unresolved classification facets before selecting domain frameworks."
    else:
        status = "CLASSIFIED"
        next_action = "Use the classified facets to select applicable requirements and domain frameworks."

    return {
        "status": status,
        "facets": ordered_facets,
        "taxonomy_references": sorted(taxonomy_references),
        "risk_flags": sorted(risk_flags),
        "unresolved_facets": unresolved,
        "conditional_candidates": conditional_candidates,
        "evidence": [],
        "next_action": next_action,
    }


def determine_execution_depth(
    *, steps: int = 1, risk: str = "low", external_action: bool = False, ambiguity: bool = False
) -> str:
    if risk == "critical" or (external_action and risk == "high"):
        return "L4"
    if risk == "high" or steps >= 8:
        return "L3"
    if steps >= 4 or external_action or ambiguity:
        return "L2"
    if steps >= 2:
        return "L1"
    return "L0"


def align_domain_practices(
    domain: str,
    frameworks: Iterable[dict[str, Any]],
    *,
    substantive: bool = True,
    verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve authoritative domain practices without inventing compliance.

    A substantive task must either select applicable international standards or
    professional frameworks, or expose an explicit research requirement. L0
    work can skip this control when no domain framework could affect the result.
    """
    if not substantive:
        return {
            "domain": domain,
            "status": "NOT_REQUIRED",
            "frameworks": [],
            "compliance": "NOT_ASSESSED",
            "deviations": [],
            "next_action": None,
        }

    candidates = [
        item
        for item in frameworks
        if item.get("status") == "active"
        and item.get("authority") in FRAMEWORK_AUTHORITIES
        and item.get("official_source")
        and (domain in item.get("domains", []) or "cross-domain" in item.get("domains", []))
    ]
    candidates.sort(
        key=lambda item: (
            domain not in item.get("domains", []),
            -item.get("priority", 0),
            item["id"],
        )
    )
    if not candidates:
        return {
            "domain": domain,
            "status": "RESEARCH_REQUIRED",
            "frameworks": [],
            "compliance": "UNVERIFIED",
            "deviations": [],
            "next_action": "Identify current authoritative international standards and professional frameworks for this domain.",
        }

    verified = bool(
        verification
        and verification.get("passed")
        and verification.get("evidence")
    )
    return {
        "domain": domain,
        "status": "ALIGNED",
        "frameworks": [item["id"] for item in candidates],
        "versions": {item["id"]: item.get("version", "current-official") for item in candidates},
        "sources": {item["id"]: item["official_source"] for item in candidates},
        "applicability": {item["id"]: "APPLICABLE_PENDING_TAILORING" for item in candidates},
        "compliance": "VERIFIED" if verified else "UNVERIFIED",
        "deviations": [],
        "next_action": None,
    }


def build_plan(tasks: Iterable[dict[str, Any]]) -> list[str]:
    """Return a stable topological order or reject unresolved/cyclic graphs."""
    records = {item["id"]: item for item in tasks}
    indegree = {task_id: 0 for task_id in records}
    dependents: dict[str, list[str]] = defaultdict(list)
    for task_id, record in records.items():
        for dependency in record.get("dependencies", []):
            if dependency not in records:
                raise KeyError(f"unresolved dependency: {dependency}")
            indegree[task_id] += 1
            dependents[dependency].append(task_id)
    ready = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
    ordered: list[str] = []
    while ready:
        task_id = ready.popleft()
        ordered.append(task_id)
        for dependent in sorted(dependents[task_id]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    if len(ordered) != len(records):
        raise ValueError("execution graph contains a cycle")
    return ordered


def select_next_work_unit(
    tasks: Iterable[dict[str, Any]], *, plan_id: str, plan_status: str,
    clarification_status: str = "NOT_REQUIRED",
) -> str | None:
    """Return the single active or next ready atomic work unit.

    User-visible work has a work-in-progress limit of one. Implementations may
    batch safe read-only operations inside that unit, but may not expose two
    active completion targets or bypass dependency completion.
    """
    if not plan_id.strip():
        raise ValueError("execution requires a concrete plan identifier")
    if plan_status != "READY":
        raise ValueError("execution requires a READY plan")
    if clarification_status == "PENDING":
        raise ValueError("material clarification must be resolved before execution")
    if clarification_status not in {"NOT_REQUIRED", "RESOLVED"}:
        raise ValueError("invalid clarification status")

    records = list(tasks)
    by_id = {item["id"]: item for item in records}
    if len(by_id) != len(records):
        raise ValueError("work unit identifiers must be unique")

    completed = {item["id"] for item in records if item.get("status") == "COMPLETED"}
    for item in records:
        for dependency in item.get("dependencies", []):
            if dependency not in by_id:
                raise KeyError(f"unresolved dependency: {dependency}")

    active_records = [item for item in records if item.get("status") == "ACTIVE"]
    active = [item["id"] for item in active_records]
    if len(active) > 1:
        raise ValueError("atomic execution allows only one active work unit")
    if active:
        if not set(active_records[0].get("dependencies", [])).issubset(completed):
            raise ValueError("active work unit has incomplete dependencies")
        return active[0]

    for item in records:
        dependencies = item.get("dependencies", [])
        if item.get("status") == "PENDING" and set(dependencies).issubset(completed):
            return item["id"]
    return None


def route_capability(requirement: str, capabilities: Iterable[dict[str, Any]]) -> dict[str, Any]:
    authority = {"user": 6, "connected": 5, "official": 4, "canonical": 3, "secondary": 2, "community": 1, "model": 0}
    candidates = [item for item in capabilities if item.get("available", True)
                  and requirement in item.get("capabilities", [])
                  and item.get("permission", "read") != "denied"]
    if not candidates:
        raise LookupError(f"no available capability satisfies {requirement}")
    return max(candidates, key=lambda item: (
        authority.get(item.get("authority", "model"), -1),
        -item.get("risk", 0), -item.get("latency", 0), item["id"],
    ))


def select_output_profile(
    task_classes: Iterable[str],
    profiles: Iterable[dict[str, Any]],
    *,
    requested_id: str | None = None,
    machine_readable: bool = False,
) -> dict[str, Any]:
    """Select a lightweight output contract while preserving user choice."""
    active = [item for item in profiles if item.get("status") == "active"]
    if requested_id:
        for item in active:
            if item.get("id") == requested_id:
                return deepcopy(item)
        raise LookupError(f"requested output profile is unavailable: {requested_id}")

    if machine_readable:
        candidates = [item for item in active if item.get("machine_readable") is True]
        if not candidates:
            raise LookupError("no active machine-readable output profile")
    else:
        classes = set(task_classes)
        candidates = [
            item for item in active
            if classes & set(item.get("task_classes", item.get("applies_to", [])))
        ]
        if not candidates:
            candidates = [item for item in active if item.get("id") == "output.answer-concise"]
        if not candidates:
            raise LookupError("no applicable output profile")

    selected = sorted(
        candidates,
        key=lambda item: (-item.get("priority", 0), item["id"]),
    )[0]
    return deepcopy(selected)


def validate_output_record(record: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Validate only the material fields declared by an output profile."""
    errors: list[str] = []
    if record.get("profile") != profile.get("id"):
        errors.append("profile does not match the selected output contract")

    for field_name in profile.get("required_fields", []):
        value = record.get(field_name)
        if value is None or value == "" or value == [] or value == {}:
            errors.append(f"required output field is missing or empty: {field_name}")

    return {
        "profile": profile.get("id"),
        "valid": not errors,
        "errors": errors,
    }


def verify_evidence(record: dict[str, Any], verification: dict[str, Any] | None = None) -> dict[str, Any]:
    result = deepcopy(record)
    evidence_class = result.get("class", "UNKNOWN")
    if evidence_class not in EVIDENCE_CLASSES:
        raise ValueError(f"invalid evidence class: {evidence_class}")
    if verification and verification.get("passed") and verification.get("provenance"):
        result["class"] = "VERIFIED"
        result["verification"] = deepcopy(verification)
    return result


def require_approval(action: str, approval: dict[str, Any] | None = None) -> bool:
    if action not in HIGH_IMPACT_ACTIONS:
        return True
    if not approval or approval.get("status") != "APPROVED" or action not in approval.get("scope", []):
        raise ApprovalRequired(f"{action} requires scoped approval")
    return True


def can_transition_release(current: str, target: str, open_blockers: Iterable[str]) -> bool:
    if target not in RELEASE_TRANSITIONS.get(current, set()):
        return False
    if target == "RELEASED" and list(open_blockers):
        return False
    return True


def _timestamp_now(timezone_name: str) -> str:
    try:
        timezone = ZoneInfo(timezone_name)
    except (KeyError, ValueError) as error:
        raise ValueError(f"unknown timezone: {timezone_name}") from error
    return datetime.now(timezone).isoformat(timespec="seconds")


def prepare_library_record(
    output_id: str,
    profile: dict[str, Any],
    *,
    requested_format: str | None = None,
    library_root: str = "library",
    capability_available: bool = True,
    authorized: bool = True,
    sensitivity_allowed: bool = True,
    timestamp: str | None = None,
    timezone_name: str = "UTC",
) -> dict[str, Any]:
    """Plan a canonical output location without claiming it has been saved."""
    output_format = requested_format or profile.get("format")
    supported_formats = set(profile.get("supported_formats", []))
    if output_format not in supported_formats:
        raise ValueError(f"unsupported output format for {profile.get('id')}: {output_format}")

    collection = profile.get("library_collection")
    if not isinstance(collection, str) or not re.fullmatch(r"[a-z0-9-]+", collection):
        raise ValueError("output profile requires a safe library collection")
    extensions = profile.get("file_extensions", {})
    extension = extensions.get(output_format) or profile.get("file_extension")
    if not isinstance(extension, str) or not re.fullmatch(r"[a-z0-9]+", extension):
        raise ValueError(f"output profile lacks a safe extension for {output_format}")

    root = PurePosixPath(library_root)
    if root.is_absolute() or not root.parts or any(part in {"", ".", ".."} for part in root.parts):
        raise ValueError("library root must be a safe relative path")

    safe_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", output_id).strip(".-")
    if not safe_id:
        raise ValueError("output identifier must contain a safe filename character")

    if not capability_available:
        delivery_status = "CAPABILITY_UNAVAILABLE"
    elif not authorized or not sensitivity_allowed:
        delivery_status = "BLOCKED"
    else:
        delivery_status = "READY"

    location = None
    if delivery_status == "READY":
        location = str(PurePosixPath(library_root) / collection / f"{safe_id}.{extension}")

    generated_at = timestamp or _timestamp_now(timezone_name)
    return {
        "id": output_id,
        "namespace": "CANONICAL_LIBRARY",
        "version": "1",
        "timestamp": generated_at,
        "timezone": timezone_name,
        "provenance": {"output_profile": profile.get("id", "unknown")},
        "status": "ACTIVE",
        "delivery_status": delivery_status,
        "dependencies": [],
        "replaces": None,
        "format": output_format,
        "collection": collection,
        "location": location,
        "persistence_evidence": None,
    }


def confirm_library_save(record: dict[str, Any], receipt: PersistenceReceipt) -> dict[str, Any]:
    """Mark a planned library record saved only after durable-write evidence exists."""
    if record.get("delivery_status") != "READY" or not record.get("location"):
        raise ValueError("only a READY library record can be confirmed saved")
    if not isinstance(receipt, PersistenceReceipt):
        raise ValueError("a validated persistence receipt is required before claiming SAVED")
    if receipt.location != record["location"]:
        raise ValueError("persistence receipt location does not match the planned record")
    saved = deepcopy(record)
    saved["delivery_status"] = "SAVED"
    saved["persistence_evidence"] = {
        "adapter": receipt.adapter,
        "location": receipt.location,
        "checksum": receipt.checksum,
        "bytes_written": receipt.bytes_written,
        "verified_at": receipt.verified_at,
    }
    return saved


def create_dashboard(
    objective: str, *, plan_id: str, plan_status: str, progress: int = 0,
    active_stage: str = "INTAKE",
    active_unit: str | None = None, completed_units: int = 0, total_units: int = 1,
    blocker: str | None = None, library: dict[str, Any] | str | None = None,
    substantive: bool = True, quality_gate: str = "PENDING",
    performance_mode: str = "LEAN", timestamp: str | None = None,
    timezone_name: str = "UTC", duration_ms: int = 0,
    input_summary: str | None = None, processing_summary: str = "Plan initialized",
    output_summary: str = "Pending", goal: str | None = None, task: str | None = None,
    playbook: str = "Direct response", frameworks: Iterable[str] = ("ATLAS execution spine",),
    sop: str = "Plan → execute → verify → persist → deliver",
    output_profile: str = "output.answer-concise", surface: str = "core",
    clarification_status: str = "NOT_REQUIRED",
) -> dict[str, Any]:
    if not plan_id.strip():
        raise ValueError("dashboard requires a concrete plan identifier")
    if not 0 <= progress <= 100:
        raise ValueError("progress must be between 0 and 100")
    if total_units < 1 or not 0 <= completed_units <= total_units:
        raise ValueError("work-unit progress is invalid")
    if quality_gate not in {"PENDING", "PASS", "FAIL", "BLOCKED"}:
        raise ValueError("invalid quality gate")
    if performance_mode != "LEAN":
        raise ValueError("unsupported performance mode")
    if duration_ms < 0:
        raise ValueError("duration_ms cannot be negative")
    if plan_status not in {"DRAFT", "READY", "BLOCKED"}:
        raise ValueError("invalid plan status")
    if clarification_status not in {"NOT_REQUIRED", "PENDING", "RESOLVED"}:
        raise ValueError("invalid clarification status")
    if surface not in {"core", "chatgpt", "codex", "work"}:
        raise ValueError("unsupported surface")
    framework_list = list(dict.fromkeys(frameworks))
    if not framework_list:
        framework_list = ["Not applicable"]
    if library is None or isinstance(library, str):
        library_state = {
            "status": "PENDING",
            "location": None,
            "format": "markdown",
            "record_id": None,
        }
    else:
        library_state = {
            "status": library.get("delivery_status", library.get("status", "PENDING")),
            "location": library.get("location"),
            "format": library.get("format", "markdown"),
            "record_id": library.get("record_id", library.get("id")),
        }
    filled = min(10, max(0, round(progress / 10)))
    return {
        "system": "ATLAS", "objective": objective, "progress": progress,
        "surface": surface,
        "plan_id": plan_id,
        "timestamp": timestamp or _timestamp_now(timezone_name),
        "duration_ms": duration_ms,
        "input_summary": input_summary or objective,
        "processing_summary": processing_summary,
        "output_summary": output_summary,
        "goal": goal or objective,
        "task": task or active_unit or objective,
        "playbook": playbook,
        "frameworks": framework_list,
        "sop": sop,
        "output_profile": output_profile,
        "plan_status": plan_status,
        "clarification_status": clarification_status,
        "progress_visual": f"[{'#' * filled}{'-' * (10 - filled)}] {progress}%",
        "active_stage": active_stage, "blocker_or_approval": blocker or "None",
        "active_unit": active_unit or objective,
        "completed_units": completed_units, "total_units": total_units,
        "library": library_state, "quality_gate": quality_gate,
        "performance_mode": performance_mode,
        "execution_layer": "L1" if substantive else "L0",
    }


def render_dashboard(dashboard: dict[str, Any]) -> str:
    """Render an event-driven dashboard without exposing private reasoning."""
    library = dashboard["library"]
    library_detail = library["status"]
    if library.get("location"):
        library_detail += f" · {library['location']} ({library['format']})"
    return "\n".join((
        f"ATLAS/{dashboard['surface']} {dashboard['progress_visual']} | "
        f"{dashboard['timestamp']} | {dashboard['duration_ms']} ms",
        f"Goal {dashboard['goal']} | Task {dashboard['completed_units']}/{dashboard['total_units']} · "
        f"{dashboard['active_stage']}: {dashboard['task']}",
        f"Input {dashboard['input_summary']} | Processing {dashboard['processing_summary']}",
        f"Playbook {dashboard['playbook']} | Framework {', '.join(dashboard['frameworks'])}",
        f"SOP {dashboard['sop']} | Plan {dashboard['plan_id']}:{dashboard['plan_status']} | "
        f"Clarification {dashboard['clarification_status']}",
        f"Output {dashboard['output_summary']} | Profile {dashboard['output_profile']}",
        f"Library {library_detail}",
        f"Quality {dashboard['quality_gate']} | Blocker {dashboard['blocker_or_approval']}",
    ))


@dataclass
class StateStore:
    task_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    canonical_state: dict[str, dict[str, Any]] = field(default_factory=dict)

    def save_task(self, identifier: str, value: dict[str, Any]) -> None:
        self.task_state[identifier] = deepcopy(value)

    def save_canonical(self, identifier: str, value: dict[str, Any]) -> None:
        if identifier in self.task_state:
            raise ValueError("task state cannot silently overwrite canonical state")
        self.canonical_state[identifier] = deepcopy(value)

    def archive_canonical(self, identifier: str) -> None:
        record = self.canonical_state[identifier]
        if record.get("active_dependents"):
            raise CanonicalRevisionInUse(identifier)
        record["status"] = "ARCHIVED"
