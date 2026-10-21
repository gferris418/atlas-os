"""First-stage ATLAS intent and collection-need routing.

ATLAS always remains the operating architecture. This module separates the
kind of work requested from the way external evidence should be collected.
ARGUS is activated only when ATLAS determines that structured intelligence
collection is materially required.

`route` is retained as a compatibility projection for existing hosts. The
authoritative ARGUS activation field is `collection_mode`.
"""

from __future__ import annotations

import re
from typing import Any, Iterable


COLLECTION_TYPES = (
    "TARGET_PROFILE",
    "ENTITY_DOSSIER",
    "PRODUCT_CAPABILITY",
    "BUYER_REQUIREMENT",
    "PROCUREMENT_DISCOVERY",
    "PROCUREMENT_PLAN",
    "PROJECT_PIPELINE",
    "FUNDING_BUDGET",
    "SUPPLIER_LANDSCAPE",
    "COMPETITOR_LANDSCAPE",
    "STAKEHOLDER_NETWORK",
    "INSTALLED_BASE",
    "MARKET_LANDSCAPE",
    "OPPORTUNITY_DISCOVERY",
    "MONITORING",
)


def _has(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def _direct_result(route: str, mode: str, rationale: str, confidence: float) -> dict[str, Any]:
    return {
        "route": route,
        "confidence": confidence,
        "rationale_code": rationale,
        "specialist": None,
        "capability_requirements": [],
        "intelligence_types": [],
        "domain_context_mode": "ON_DEMAND",
        "collection_mode": mode,
        "collection_required": False,
        "collection_types": [],
        "collection_depth": None,
        "collection_rationale_code": rationale,
    }


def triage_request(text: str, *, task_classes: Iterable[str] | None = None) -> dict[str, Any]:
    """Return task-route compatibility plus the authoritative collection decision.

    Collection modes:
      NONE             no external collection is needed;
      ATLAS_DIRECT     ordinary retrieval/research stays in ATLAS;
      ARGUS_COLLECTION structured collection is delegated to ARGUS;
      HYBRID           ARGUS collects while ATLAS retains analysis/decision work.
    """

    raw = " ".join(text.split())
    normalized = raw.lower()
    classes = set(task_classes or ())

    analytical_signal = bool(classes & {"ANALYSIS", "DECISION"}) or _has(normalized, (
        r"\bcompare\b", r"\bassess\b", r"\bevaluate\b", r"\banaly[sz]e\b",
        r"\bforecast\b", r"\bpredict\b", r"\blikely\b", r"\bprobability\b",
        r"\brank\b", r"\bprioriti[sz]e\b", r"\bshould we\b", r"\brecommend\b",
    ))
    monitor_signal = bool(classes & {"MONITORING"}) or _has(normalized, (
        r"\bmonitor\b", r"\bwatch for\b", r"\btrack developments\b", r"\balert.*when\b",
    ))

    policy_or_rules = _has(normalized, (
        r"\bpolicy\b", r"\bregulation(?:s)?\b", r"\brules?\b", r"\bcircular(?:s)?\b",
        r"\blaw\b", r"\blegal framework\b", r"\bguideline(?:s)?\b",
    ))
    explicit_collection_language = _has(normalized, (
        r"\bprocurement plan\b", r"\bannual procurement\b", r"\bprocurement pipeline\b",
        r"\bproject pipeline\b", r"\bopportunit(?:y|ies)\b", r"\binstalled base\b",
        r"\bcompetitor(?:s| landscape)?\b", r"\bsupplier landscape\b",
        r"\bstakeholder(?:s| network)?\b", r"\bmarket landscape\b", r"\bdossier\b",
        r"\bprofile (?:of|on)\b", r"\bdecision maker(?:s)?\b",
    ))

    # Transformations of material already supplied by the user are not collection
    # missions even if the document subject contains procurement or intelligence terms.
    supplied_material = _has(normalized, (
        r"\battached\b", r"\buploaded\b", r"\bprovided\b", r"\bthis (?:document|file|text|plan|report)\b",
    ))
    transformation = bool(classes & {"WRITING", "DOCUMENT", "DATA", "CODING", "DEBUGGING"}) or _has(normalized, (
        r"\b(?:summari[sz]e|rewrite|draft|write|translate|convert|calculate|compute|debug|fix|edit|format|proofread)\b",
    ))
    if supplied_material and transformation:
        return _direct_result("GENERAL_TASK", "NONE", "SUPPLIED_MATERIAL_TRANSFORMATION", 0.99)

    # Policy/regulatory subject analysis is ATLAS work unless the request separately
    # asks for a structured target, procurement, landscape, or monitoring mission.
    if policy_or_rules and not explicit_collection_language and not monitor_signal:
        return _direct_result("GENERAL_SEARCH", "ATLAS_DIRECT", "POLICY_OR_RULES_DIRECT", 0.97)

    collection_types: list[str] = []

    procurement_plan = _has(normalized, (
        r"\b(?:annual )?procurement plan\b", r"\bprocurement pipeline\b",
        r"\bplanned procurement(?:s)?\b", r"\bacquisition plan\b",
    ))
    if procurement_plan:
        collection_types.extend(["PROCUREMENT_PLAN", "PROCUREMENT_DISCOVERY"])

    # Forecasting future procurements needs an evidence-collection leg even though
    # the forecast itself remains ATLAS analysis.
    future_procurement = analytical_signal and _has(normalized, (
        r"\bprocurement(?:s)?\b", r"\bprocure(?:ment|ments)?\b", r"\bacquisition(?:s)?\b",
    )) and _has(normalized, (
        r"\bforecast\b", r"\bpredict\b", r"\blikely\b", r"\bnext\b", r"\bover\s+\d+\s+(?:month|year)s?\b",
    ))
    if future_procurement:
        collection_types.append("PROCUREMENT_DISCOVERY")

    project_pipeline = _has(normalized, (
        r"\bproject pipeline\b", r"\bprogramme pipeline\b", r"\bprogram pipeline\b",
    ))
    if project_pipeline:
        collection_types.append("PROJECT_PIPELINE")

    opportunity_signal = _has(normalized, (
        r"\bopportunit(?:y|ies)\b", r"\bprocurement opportunity\b", r"\btender pipeline\b",
        r"\bwhat .* (?:buy|procure|acquire)\b",
    ))
    if opportunity_signal:
        collection_types.extend(["OPPORTUNITY_DISCOVERY", "PROCUREMENT_DISCOVERY"])

    buyer_cue = _has(normalized, (
        r"\bbangladesh (?:navy|army|air force|coast guard)\b", r"\bbadc\b",
        r"\bministry\b", r"\bdirectorate\b", r"\bauthority\b", r"\bcorporation\b",
    ))
    product_for_buyer = buyer_cue and _has(
        normalized, (r".+\bfor\b.+", r"\bsupply\b.+", r"\bprocure\b.+", r"\bassess\b.+")
    )
    if product_for_buyer and not policy_or_rules:
        collection_types.extend(["BUYER_REQUIREMENT", "PRODUCT_CAPABILITY", "OPPORTUNITY_DISCOVERY"])

    if _has(normalized, (
        r"\bcompetitive landscape\b",
        r"\bcompetitor landscape\b",
        r"\bcompetitors\b.*\b(?:market|landscape|identify|find|list|compare|map)\b",
        r"\b(?:identify|find|list|compare|map)\b.*\bcompetitors\b",
    )):
        collection_types.append("COMPETITOR_LANDSCAPE")
    if _has(normalized, (
        r"\bsupplier landscape\b",
        r"\bvendor landscape\b",
        r"\bsuppliers\b.*\b(?:market|landscape|identify|find|list|compare|map)\b",
        r"\b(?:identify|find|list|compare|map)\b.*\bsuppliers\b",
    )):
        collection_types.append("SUPPLIER_LANDSCAPE")
    if _has(normalized, (
        r"\bstakeholder(?:s| network)?\b", r"\bdecision maker(?:s)?\b", r"\binfluence map\b",
    )):
        collection_types.append("STAKEHOLDER_NETWORK")
    if _has(normalized, (r"\binstalled base\b", r"\bexisting fleet\b", r"\bexisting system(?:s)?\b")):
        collection_types.append("INSTALLED_BASE")
    if _has(normalized, (r"\bmarket landscape\b", r"\bmarket participants\b", r"\bmarket map\b")):
        collection_types.append("MARKET_LANDSCAPE")
    if _has(normalized, (r"\bfunding\b", r"\bbudget allocation\b", r"\bdevelopment partner\b")) and explicit_collection_language:
        collection_types.append("FUNDING_BUDGET")
    if monitor_signal:
        collection_types.append("MONITORING")

    # A bare strategic/commercial target is a collection request even without an
    # analytical verb. Digits alone never establish a target; uppercase identifiers
    # must contain alphabetic characters, and ordinary operation verbs win first.
    explanatory_question = _has(normalized, (
        r"^(?:what|who|when|where|why|how)\b", r"^explain\b", r"^define\b", r"^summari[sz]e\b",
    ))
    company_cue = _has(normalized, (
        r"\bengineering\b", r"\bsystems?\b", r"\btechnolog(?:y|ies)\b", r"\bindustries\b",
        r"\bholdings\b", r"\bgroup\b", r"\baerospace\b", r"\bshipyard\b", r"\bsolutions\b",
        r"\blimited\b", r"\bltd\b", r"\bplc\b", r"\binc\b", r"\bcorp\b", r"\bgmbh\b",
        r"\bag\b", r"\bsa\b", r"\boy\b", r"\bllc\b", r"\bfzco\b",
    ))
    raw_words = raw.split()
    uppercase_identifier = any(
        token.isupper() and len(token) > 1 and any(ch.isalpha() for ch in token)
        for token in raw_words
    )
    no_action_verb = not _has(normalized, (
        r"\b(?:find|search|explain|write|rewrite|draft|calculate|compute|convert|create|build|implement|fix|debug|update|edit|translate|discuss|summari[sz]e|format|proofread)\b",
    ))
    bare_named_target = (
        1 <= len(raw_words) <= 6
        and not explanatory_question
        and no_action_verb
        and not policy_or_rules
        and (company_cue or uppercase_identifier)
    )
    if bare_named_target:
        collection_types.extend(["TARGET_PROFILE", "ENTITY_DOSSIER"])

    if _has(normalized, (r"\bprofile (?:of|on)\b", r"\bdossier (?:of|on)\b")):
        collection_types.extend(["TARGET_PROFILE", "ENTITY_DOSSIER"])

    collection_types = list(dict.fromkeys(collection_types))
    collection_required = bool(collection_types)

    if collection_required:
        collection_mode = "HYBRID" if analytical_signal else "ARGUS_COLLECTION"
        if "MONITORING" in collection_types:
            collection_depth = "C4_MONITOR"
        elif set(collection_types) & {
            "PROCUREMENT_PLAN", "PROCUREMENT_DISCOVERY", "OPPORTUNITY_DISCOVERY",
            "BUYER_REQUIREMENT", "FUNDING_BUDGET", "PROJECT_PIPELINE",
        }:
            collection_depth = "C3_OPPORTUNITY"
        elif set(collection_types) & {
            "ENTITY_DOSSIER", "COMPETITOR_LANDSCAPE", "SUPPLIER_LANDSCAPE",
            "STAKEHOLDER_NETWORK", "MARKET_LANDSCAPE", "INSTALLED_BASE",
        }:
            collection_depth = "C2_DOSSIER"
        else:
            collection_depth = "C1_PROFILE"
        rationale = (
            "STRUCTURED_COLLECTION_WITH_ATLAS_ANALYSIS"
            if collection_mode == "HYBRID"
            else "STRUCTURED_COLLECTION_REQUIRED"
        )
        return {
            "route": "INTELLIGENCE",  # compatibility projection only
            "confidence": 0.96,
            "rationale_code": rationale,
            "specialist": "ARGUS",
            "capability_requirements": ["intelligence_collection"],
            "intelligence_types": [],
            "domain_context_mode": "ARGUS_ENRICHES",
            "collection_mode": collection_mode,
            "collection_required": True,
            "collection_types": collection_types,
            "collection_depth": collection_depth,
            "collection_rationale_code": rationale,
        }

    task_signal = bool(classes & {
        "ANALYSIS", "DECISION", "WRITING", "DOCUMENT", "DATA", "CODING",
        "DEBUGGING", "DESIGN", "PLANNING", "WORKFLOW", "EXTERNAL_ACTION",
    }) or _has(normalized, (
        r"\b(?:assess|evaluate|analy[sz]e|rewrite|draft|write|summari[sz]e|calculate|compute|convert|create|build|implement|fix|debug|update|edit|translate|discuss)\b",
    ))
    if task_signal:
        return _direct_result("GENERAL_TASK", "NONE", "DIRECT_TASK_EXECUTION", 0.94)

    search_signal = bool(classes & {"ANSWER", "RESEARCH"}) or _has(normalized, (
        r"\b(?:find|search|look up|lookup|current|latest|what is|who is|when is|where is|explain|research)\b",
    ))
    return _direct_result(
        "GENERAL_SEARCH" if search_signal else "GENERAL_TASK",
        "ATLAS_DIRECT" if search_signal else "NONE",
        "FACT_RETRIEVAL" if search_signal else "DIRECT_TASK_EXECUTION",
        0.90,
    )
