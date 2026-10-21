"""Fast first-stage routing for ATLAS requests.

The triage boundary is deliberately shallow: it decides whether ATLAS should
execute directly or delegate intelligence-grade work to ARGUS. Deep taxonomy,
domain classification, framework alignment, and evidence synthesis happen only
when the selected route materially requires them.
"""

from __future__ import annotations

import re
from typing import Any, Iterable


INTELLIGENCE_TYPES = (
    "STRATEGIC_INTELLIGENCE",
    "MARKET_INTELLIGENCE",
    "OPPORTUNITY_INTELLIGENCE",
    "COMPETITIVE_INTELLIGENCE",
    "STAKEHOLDER_INTELLIGENCE",
    "POLITICAL_ECONOMIC_INTELLIGENCE",
    "MONITORING_INTELLIGENCE",
    "FORECASTING_INTELLIGENCE",
    "SCENARIO_INTELLIGENCE",
    "DECISION_INTELLIGENCE",
)


def _has(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def triage_request(text: str, *, task_classes: Iterable[str] | None = None) -> dict[str, Any]:
    """Classify one request into the minimum sufficient execution route.

    This deterministic matcher is a reference fallback. A capable host may make
    the semantic decision natively, but must emit the same three route values
    and must not activate ARGUS merely because a government entity is named.
    """
    normalized = " ".join(text.lower().split())
    classes = set(task_classes or ())
    intelligence_types: list[str] = []

    opportunity_objective = _has(normalized, (
        r"\bopportunit(?:y|ies)\b.*\b(?:pursue|qualif|prioriti[sz]e|rank|capture|bid|no[- ]bid|win)\b",
        r"\b(?:pursue|qualif|prioriti[sz]e|rank|capture)\b.*\b(?:tender|rfp|procurement|opportunit(?:y|ies))\b",
        r"\b(?:assess|evaluate|analy[sz]e)\b.*\b(?:public procurement )?opportunit(?:y|ies)\b",
        r"\bopportunit(?:y|ies)\b.*\b(?:assess|evaluate|analy[sz]e)\b",
        r"\bwin probability\b",
    ))
    if opportunity_objective:
        intelligence_types.append("OPPORTUNITY_INTELLIGENCE")

    if _has(normalized, (r"\bcompetitor(?:s| intelligence)?\b", r"\bcompetitive intelligence\b", r"\bcompetitive landscape\b")):
        intelligence_types.append("COMPETITIVE_INTELLIGENCE")

    if _has(normalized, (r"\bdecision maker(?:s)?\b", r"\bstakeholder intelligence\b", r"\binfluence map\b")):
        intelligence_types.append("STAKEHOLDER_INTELLIGENCE")

    if _has(normalized, (r"\bstrategic intelligence\b", r"\bstrategic outlook\b", r"\bstrategic signal(?:s)?\b")):
        intelligence_types.append("STRATEGIC_INTELLIGENCE")

    if _has(normalized, (r"\bmarket intelligence\b", r"\bmarket outlook\b", r"\bmarket sizing\b", r"\bmarket dynamics\b")):
        intelligence_types.append("MARKET_INTELLIGENCE")

    if _has(normalized, (r"\bpolitical intelligence\b", r"\beconomic intelligence\b", r"\bpolitical risk\b", r"\bgeopolitical\b", r"\bmacroeconomic outlook\b")):
        intelligence_types.append("POLITICAL_ECONOMIC_INTELLIGENCE")

    if _has(normalized, (r"\bmonitor\b", r"\bwatch for\b", r"\btrack developments\b", r"\bsignal monitoring\b")):
        intelligence_types.append("MONITORING_INTELLIGENCE")

    if _has(normalized, (r"\bforecast\b", r"\bpredict\b", r"\blikelihood\b", r"\bprobability of\b", r"\bprobabilit(?:y|ies)\b")):
        intelligence_types.append("FORECASTING_INTELLIGENCE")

    if _has(normalized, (r"\bscenario(?:s| analysis| planning)?\b", r"\bwhat if\b")):
        intelligence_types.append("SCENARIO_INTELLIGENCE")

    decision_signal = _has(normalized, (
        r"\bshould we\b",
        r"\brecommend (?:whether|which|what)\b",
        r"\bprioriti[sz]e\b",
        r"\brank (?:them|these|the)\b",
        r"\bdecision intelligence\b",
    ))
    if decision_signal and intelligence_types:
        intelligence_types.append("DECISION_INTELLIGENCE")

    intelligence_types = list(dict.fromkeys(intelligence_types))
    if intelligence_types:
        return {
            "route": "INTELLIGENCE",
            "confidence": 0.95,
            "rationale_code": intelligence_types[0],
            "specialist": "ARGUS",
            "capability_requirements": ["intelligence_analysis"],
            "intelligence_types": intelligence_types,
            "domain_context_mode": "ARGUS_ENRICHES",
        }

    task_signal = bool(classes & {
        "WRITING", "DOCUMENT", "DATA", "CODING", "DEBUGGING", "DESIGN",
        "PLANNING", "WORKFLOW", "EXTERNAL_ACTION",
    }) or _has(normalized, (
        r"\b(?:rewrite|draft|write|summari[sz]e|calculate|compute|convert|create|build|implement|fix|debug|update|edit|translate)\b",
    ))
    if task_signal:
        return {
            "route": "GENERAL_TASK",
            "confidence": 0.94,
            "rationale_code": "DIRECT_TASK_EXECUTION",
            "specialist": None,
            "capability_requirements": [],
            "intelligence_types": [],
            "domain_context_mode": "ON_DEMAND",
        }

    search_signal = bool(classes & {"ANSWER", "RESEARCH", "ANALYSIS"}) or _has(normalized, (
        r"\b(?:find|search|look up|lookup|current|latest|what is|who is|when is|where is|explain|research)\b",
    ))
    return {
        "route": "GENERAL_SEARCH" if search_signal else "GENERAL_TASK",
        "confidence": 0.90,
        "rationale_code": "FACT_RETRIEVAL" if search_signal else "DIRECT_TASK_EXECUTION",
        "specialist": None,
        "capability_requirements": [],
        "intelligence_types": [],
        "domain_context_mode": "ON_DEMAND",
    }
