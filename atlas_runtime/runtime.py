"""Small executable reference for the normative ATLAS contracts.

The declarative specifications remain authoritative. This module exists so the
core invariants can be exercised at stable public seams.
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Iterable


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
    """Apply the W-question lens without turning it into a questionnaire."""
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
    required_facets: Iterable[str] = (),
    active_conditions: Iterable[str] = (),
) -> dict[str, Any]:
    """Classify domain context without guessing missing taxonomy codes.

    Records may use ``triggers`` for any-term matching and ``match_all`` for
    phrase-component matching. Conditional records are exposed as candidates
    until their declared context is active, so a customs code, for example,
    is not treated as applicable merely because a product was mentioned.
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
    unresolved = sorted(set(required_facets) - set(ordered_facets))
    conditional_candidates.sort(key=lambda item: item["id"])

    if not ordered_facets:
        status = "RESEARCH_REQUIRED"
        next_action = "Identify current authoritative taxonomy and classification sources for this domain."
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


def create_dashboard(
    objective: str, *, progress: int = 0, active_stage: str = "INTAKE",
    blocker: str | None = None, library: str = "Not required", substantive: bool = True,
) -> dict[str, Any] | None:
    if not substantive:
        return None
    if not 0 <= progress <= 100:
        raise ValueError("progress must be between 0 and 100")
    return {
        "system": "ATLAS", "objective": objective, "progress": progress,
        "active_stage": active_stage, "blocker_or_approval": blocker or "None",
        "library": library,
    }


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
