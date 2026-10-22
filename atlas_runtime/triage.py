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
    "NEED_GAP",
    "POLICY_DRIVER",
    "PROGRAMME_PROJECT",
    "APPROVAL_STATUS",
    "SUPPLIER_PROFILE",
    "REFERENCE_PROJECT",
    "EXPORT_FEASIBILITY",
    "PARTNERABILITY",
    "OPPORTUNITY_DEVELOPMENT",
    "OPPORTUNITY_MATCHING",
    "EXPANSION_DISCOVERY",
    "RAPID_TENDER",
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
        r"\bprofile (?:of|on)\b", r"\bdecision maker(?:s)?\b", r"\bcapability gap(?:s)?\b",
        r"\bunmet need(?:s)?\b", r"\bpartnerability\b", r"\bpartner with\b",
        r"\bshape (?:a |an |the )?(?:future )?opportunit(?:y|ies)\b",
        r"\bpolicy driver(?:s)?\b", r"\bproject approval\b", r"\bapproval status\b",
    ))

    supplied_material = _has(normalized, (
        r"\battached\b", r"\buploaded\b", r"\bprovided\b", r"\bthis (?:document|file|text|plan|report)\b",
    ))
    transformation = bool(classes & {"WRITING", "DOCUMENT", "DATA", "CODING", "DEBUGGING"}) or _has(normalized, (
        r"\b(?:summari[sz]e|rewrite|draft|write|translate|convert|calculate|compute|debug|fix|edit|format|proofread)\b",
    ))
    independent_collection_leg = monitor_signal or _has(normalized, (
        r"\b(?:then|and then|also)\s+(?:monitor|watch|track|find|search|identify|profile|map)\b",
        r"\b(?:then|and then|also)\b.*\b(?:procurement|opportunit(?:y|ies)|competitors?|suppliers?|stakeholders?|oems?)\b",
    ))
    if supplied_material and transformation and not independent_collection_leg:
        return _direct_result("GENERAL_TASK", "NONE", "SUPPLIED_MATERIAL_TRANSFORMATION", 0.99)

    if policy_or_rules and not explicit_collection_language and not monitor_signal:
        return _direct_result("GENERAL_SEARCH", "ATLAS_DIRECT", "POLICY_OR_RULES_DIRECT", 0.97)

    collection_types: list[str] = []

    procurement_plan = _has(normalized, (
        r"\b(?:annual )?procurement plan\b", r"\bprocurement pipeline\b",
        r"\bplanned procurement(?:s)?\b", r"\bacquisition plan\b",
    ))
    if procurement_plan:
        collection_types.extend(["PROCUREMENT_PLAN", "PROCUREMENT_DISCOVERY"])

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
        collection_types.extend(["PROJECT_PIPELINE", "PROGRAMME_PROJECT"])

    opportunity_signal = _has(normalized, (
        r"\bopportunit(?:y|ies)\b", r"\bprocurement opportunity\b", r"\btender pipeline\b",
        r"\bwhat .* (?:buy|procure|acquire)\b",
    ))
    if opportunity_signal:
        collection_types.append("OPPORTUNITY_DISCOVERY")
        if _has(normalized, (r"\bprocurement\b", r"\btender pipeline\b", r"\bprocure\b", r"\bacquisition\b")):
            collection_types.append("PROCUREMENT_DISCOVERY")

    buyer_cue = _has(normalized, (
        r"\bbangladesh (?:navy|army|air force|coast guard|railway)\b", r"\bbadc\b",
        r"\bministry\b", r"\bdirectorate\b", r"\bauthority\b", r"\bcorporation\b",
        r"\bgovernment\b", r"\bpublic sector\b",
    ))
    product_for_buyer = buyer_cue and _has(
        normalized, (r".+\bfor\b.+", r"\bsupply\b.+", r"\bprocure\b.+", r"\bassess\b.+")
    )
    if product_for_buyer and not policy_or_rules:
        collection_types.extend(["BUYER_REQUIREMENT", "PRODUCT_CAPABILITY", "OPPORTUNITY_DISCOVERY"])

    need_gap_signal = _has(normalized, (
        r"\bcapability gap(?:s)?\b", r"\bunmet need(?:s)?\b", r"\boperational gap(?:s)?\b",
        r"\bwhat (?:problem|problems|need|needs)\b", r"\bgovernment problem(?:s)?\b",
        r"\bmoderni[sz]ation need(?:s)?\b", r"\baddress with (?:foreign|international) technolog(?:y|ies)\b",
    ))
    if need_gap_signal and buyer_cue:
        collection_types.extend(["NEED_GAP", "BUYER_REQUIREMENT", "OPPORTUNITY_DISCOVERY"])
    elif need_gap_signal and opportunity_signal:
        collection_types.extend(["NEED_GAP", "OPPORTUNITY_DISCOVERY"])

    opportunity_development = _has(normalized, (
        r"\bshape (?:a |an |the )?(?:future )?opportunit(?:y|ies)\b",
        r"\bcreate (?:a |an )?(?:future )?opportunit(?:y|ies)\b",
        r"\bintroduce (?:an |a )?internationally proven solution\b",
        r"\bintroduce .*\bsolution\b.*\bgovernment\b",
        r"\bpropose .*\b(?:government|agency|public sector)\b",
        r"\bmarket development\b.*\b(?:government|public sector)\b",
    ))
    if opportunity_development:
        collection_types.extend(["NEED_GAP", "OPPORTUNITY_DEVELOPMENT", "OPPORTUNITY_DISCOVERY"])

    supply_first_discovery = _has(normalized, (
        r"\bwhere could\b.*\b(?:technology|solution|product|system|platform)\b.*\b(?:government|public sector|bangladesh)\b",
        r"\bwhich (?:government )?(?:agencies|buyers|institutions) could (?:use|need|adopt)\b",
        r"\bmap .*\b(?:technology|solution|product)\b.*\b(?:government|public sector)\b",
    ))
    if supply_first_discovery:
        collection_types.extend(["PRODUCT_CAPABILITY", "OPPORTUNITY_MATCHING", "OPPORTUNITY_DISCOVERY"])

    supplier_matching = _has(normalized, (
        r"\b(?:rank|find|identify|shortlist|compare)\b.*\b(?:oems?|suppliers?|vendors?|contractors?)\b.*\b(?:for|against)\b",
        r"\bsuitable (?:international )?(?:oems?|suppliers?|vendors?|contractors?)\b",
        r"\bmatch .*\b(?:oems?|suppliers?|vendors?|contractors?)\b",
    ))
    if supplier_matching:
        collection_types.extend(["SUPPLIER_LANDSCAPE", "OPPORTUNITY_MATCHING"])

    partnerability_signal = _has(normalized, (
        r"\bpartner with (?:us|access asia)\b", r"\brepresent(?:ation|ative| them)?\b",
        r"\b(?:local )?(?:agent|distributor)\b", r"\bexclusive (?:agent|distributor|partner)\b",
        r"\bpartnerability\b", r"\bwilling(?:ness)? to partner\b",
    ))
    if partnerability_signal and _has(normalized, (r"\boems?\b", r"\bsuppliers?\b", r"\bvendors?\b", r"\bcontractors?\b", r"\bpartner\b")):
        collection_types.append("PARTNERABILITY")

    supplier_profile_signal = _has(normalized, (
        r"\bsupplier profile\b", r"\boem profile\b", r"\bprofile .*\b(?:supplier|oem|vendor|contractor)\b",
    ))
    if supplier_profile_signal:
        collection_types.append("SUPPLIER_PROFILE")

    reference_project_signal = _has(normalized, (
        r"\breference project(?:s)?\b", r"\bsimilar project(?:s)?\b", r"\bgovernment references?\b",
    ))
    if reference_project_signal:
        collection_types.append("REFERENCE_PROJECT")

    export_signal = _has(normalized, (
        r"\bexport feasibility\b", r"\bexport control(?:s)?\b", r"\bexportable\b", r"\bexport permit(?:s)?\b",
    ))
    if export_signal and _has(normalized, (r"\boem\b", r"\bsupplier\b", r"\btechnology\b", r"\bproduct\b", r"\bsolution\b")):
        collection_types.append("EXPORT_FEASIBILITY")

    policy_driver_signal = _has(normalized, (
        r"\bpolicy driver(?:s)?\b", r"\bpolic(?:y|ies) .*\b(?:create|generate|drive)\b.*\bopportunit(?:y|ies)\b",
    ))
    if policy_driver_signal:
        collection_types.extend(["POLICY_DRIVER", "OPPORTUNITY_DISCOVERY"])

    programme_project_signal = _has(normalized, (
        r"\b(?:programme|program|project) (?:formation|concept|planning|pipeline)\b",
        r"\bfeasibility stud(?:y|ies)\b", r"\bdpp\b", r"\btapp\b",
    ))
    if programme_project_signal and (buyer_cue or opportunity_signal or monitor_signal):
        collection_types.append("PROGRAMME_PROJECT")

    approval_signal = _has(normalized, (
        r"\bproject approval\b", r"\badministrative approval\b", r"\bapproval status\b",
        r"\bapproved project(?:s)?\b", r"\bgovernment approval\b",
    ))
    if approval_signal and (buyer_cue or opportunity_signal or monitor_signal):
        collection_types.extend(["APPROVAL_STATUS", "PROGRAMME_PROJECT"])

    rapid_tender_signal = _has(normalized, (
        r"\btender (?:is )?published\b", r"\blive tender\b", r"\btender id\b", r"\bsolicitation (?:is )?published\b",
    )) and _has(normalized, (
        r"\bclos(?:e|es|ing)\b", r"\bdeadline\b", r"\beligib(?:le|ility)\b",
        r"\boems?\b", r"\bsuppliers?\b", r"\bvendors?\b", r"\bdisqualif(?:y|ier|ication)\b",
    ))
    if rapid_tender_signal:
        collection_types.extend(["RAPID_TENDER", "PROCUREMENT_DISCOVERY"])
        if _has(normalized, (r"\boems?\b", r"\bsuppliers?\b", r"\bvendors?\b", r"\bcontractors?\b")):
            collection_types.extend(["SUPPLIER_LANDSCAPE", "OPPORTUNITY_MATCHING"])

    expansion_signal = _has(normalized, (
        r"\bfollow[- ]on\b", r"\bupgrade(?:s)?\b", r"\badditional units?\b", r"\bspares?\b",
        r"\bmaintenance\b", r"\btraining opportunit(?:y|ies)\b", r"\breplacement\b", r"\bexpansion\b",
    )) and _has(normalized, (r"\bexisting\b", r"\bproject\b", r"\bcontract\b", r"\binstalled\b", r"\bfleet\b", r"\bsystem\b"))
    if expansion_signal:
        collection_types.extend(["EXPANSION_DISCOVERY", "INSTALLED_BASE", "OPPORTUNITY_DISCOVERY"])

    if _has(normalized, (
        r"\bcompetitive landscape\b",
        r"\bcompetitor landscape\b",
        r"\bcompetitors\b.*\b(?:market|landscape|identify|find|list|compare|map)\b",
        r"\b(?:identify|find|list|compare|map)\b.*\bcompetitors\b",
    )):
        collection_types.append("COMPETITOR_LANDSCAPE")
    if _has(normalized, (
        r"\bsupplier landscape\b", r"\bvendor landscape\b", r"\boem landscape\b",
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
            "BUYER_REQUIREMENT", "FUNDING_BUDGET", "PROJECT_PIPELINE", "NEED_GAP",
            "POLICY_DRIVER", "PROGRAMME_PROJECT", "APPROVAL_STATUS", "OPPORTUNITY_DEVELOPMENT",
            "OPPORTUNITY_MATCHING", "EXPANSION_DISCOVERY", "RAPID_TENDER",
        }:
            collection_depth = "C3_OPPORTUNITY"
        elif set(collection_types) & {
            "ENTITY_DOSSIER", "COMPETITOR_LANDSCAPE", "SUPPLIER_LANDSCAPE",
            "STAKEHOLDER_NETWORK", "MARKET_LANDSCAPE", "INSTALLED_BASE", "SUPPLIER_PROFILE",
            "REFERENCE_PROJECT", "EXPORT_FEASIBILITY", "PARTNERABILITY",
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
            "route": "INTELLIGENCE",
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
