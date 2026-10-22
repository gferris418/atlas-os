from __future__ import annotations

import re
from typing import Any, Iterable

from .models import RouteDecision


PRE_EXECUTION_FLOW = (
    "UNDERSTAND_AND_NORMALIZE",
    "MINIMAL_DOMAIN_FRAMING",
    "ROUTE",
)

ARGUS_APPROVAL = "ARGUS_ACTIVATION"
EXTERNAL_ACTION_APPROVAL = "EXTERNAL_ACTION"


def normalize_objective(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def minimal_domain_framing(text: str) -> dict[str, Any]:
    lower = text.lower()
    risk_flags: list[str] = []
    if any(token in lower for token in ("navy", "military", "defence", "defense", "radar", "weapon")):
        risk_flags.append("defense_or_dual_use")
    if any(token in lower for token in ("contract", "agreement", "legal")):
        risk_flags.append("legal_or_commercial")
    jurisdiction = "Bangladesh" if "bangladesh" in lower else None
    return {
        "jurisdiction": jurisdiction,
        "risk_flags": risk_flags,
        "unresolved": [],
        "principle": "minimal_sufficient_context",
    }


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _approval(status_key: str, approvals: tuple[str, ...]) -> tuple[bool, str]:
    return True, "APPROVED" if status_key in approvals else "PENDING"


def choose_route(objective: str, approvals: tuple[str, ...] = ()) -> RouteDecision:
    text = normalize_objective(objective)
    lower = text.lower()

    if _contains_any(lower, ("send this", "send the", "publish", "purchase", "buy ", "delete ", "remove access", "change permission")):
        required, status = _approval(EXTERNAL_ACTION_APPROVAL, approvals)
        return RouteDecision(
            "EXTERNAL_ACTION", "external_action", "host.external-action", required, status,
            "The request changes external state and therefore remains approval-gated.",
        )

    if _contains_any(lower, ("my email", "our email", "my calendar", "our sharepoint", "our files", "hubspot", "slack", "our crm")):
        return RouteDecision(
            "CONNECTED_SOURCE", "connected_source", "host.connected-source", False, "NOT_REQUIRED",
            "The answer depends on an authorized private or connected source.",
        )

    if _contains_any(lower, ("debug ", "write code", "implement ", "python", "sql query", "run code", "calculate with data")):
        return RouteDecision(
            "CODE_EXECUTION", "code_execution", "host.code", False, "NOT_REQUIRED",
            "The request materially benefits from deterministic code execution.",
        )

    if _contains_any(lower, ("compare ", "forecast likely", "scenario", "rank suppliers")) and _contains_any(
        lower, ("opportunit", "procurement", "supplier", "competitor", "market")
    ):
        required, status = _approval(ARGUS_APPROVAL, approvals)
        return RouteDecision(
            "MULTI_CAPABILITY", "intelligence_collection+analysis", "argus+atlas", required, status,
            "Structured collection is needed, but ATLAS retains the comparison, forecast, scenario, or decision work.",
        )

    argus_signals = (
        "dossier", "opportunity footprint", "procurement plan", "project pipeline", "supplier landscape",
        "competitor landscape", "stakeholder network", "installed base", "monitor ", "opportunity discovery",
        "target profile", "build a profile", "st engineering",
    )
    if _contains_any(lower, argus_signals):
        required, status = _approval(ARGUS_APPROVAL, approvals)
        return RouteDecision(
            "ARGUS", "intelligence_collection", "argus", required, status,
            "The request requires bounded structured intelligence collection rather than a simple lookup.",
        )

    if _contains_any(lower, ("current", "latest", "today", "live ", "find ", "lookup", "search ", "price", "rate", "tender")):
        return RouteDecision(
            "DIRECT_SEARCH", "direct_search", "host.search", False, "NOT_REQUIRED",
            "The task is primarily current factual retrieval and does not require structured intelligence collection.",
        )

    if _contains_any(lower, ("research", "policy", "regulation", "explain", "analyze", "analyse", "investigate")):
        return RouteDecision(
            "DEEP_RESEARCH", "deep_research", "host.research", False, "NOT_REQUIRED",
            "The task calls for research or synthesis under direct ATLAS control.",
        )

    if _contains_any(lower, ("review contract", "review agreement", "legal review", "tax advice")):
        return RouteDecision(
            "SPECIALIST", "specialist_execution", "host.specialist", False, "NOT_REQUIRED",
            "The request is best handled by a bounded specialist capability.",
        )

    return RouteDecision(
        "NO_TOOL", "direct_answer", "host.native", False, "NOT_REQUIRED",
        "The request can be completed from supplied context and native model capability.",
    )
