"""Deterministic selection of ATLAS canonical capabilities.

The capability layer never decides whether ARGUS may activate. It consumes the
already-authoritative Collection-Need Gate result and selects domain reasoning
capabilities around that decision. Kernel services are always present.
"""

from __future__ import annotations

import re
from typing import Any, Iterable


KERNEL_CAPABILITIES = (
    "atlas.evidence-governance",
    "atlas.execution-governance",
    "atlas.agent-security",
    "atlas.classification-crosswalk",
)

_ARGUS_MODES = {"ARGUS_COLLECTION", "HYBRID"}
_PROCUREMENT_PRIMARY_COLLECTION_TYPES = {
    "BUYER_REQUIREMENT",
    "PROCUREMENT_DISCOVERY",
    "PROCUREMENT_PLAN",
}


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def plan_canonical_capabilities(
    objective: str,
    *,
    task_classes: Iterable[str],
    collection_mode: str,
    collection_types: Iterable[str],
) -> dict[str, Any]:
    """Return the canonical capability set for one interpreted ATLAS request."""

    text = " ".join(objective.split())
    lowered = text.lower()
    classes = tuple(dict.fromkeys(task_classes))
    collection = tuple(dict.fromkeys(collection_types))
    collection_set = set(collection)

    if collection_mode not in {"NONE", "ATLAS_DIRECT", "ARGUS_COLLECTION", "HYBRID"}:
        raise ValueError(f"unsupported collection mode: {collection_mode}")

    routed: list[str] = []
    specialist: list[str] = []
    reasons: dict[str, list[str]] = {capability: ["kernel"] for capability in KERNEL_CAPABILITIES}

    def add_routed(capability: str, reason: str) -> None:
        if capability not in routed:
            routed.append(capability)
        reasons.setdefault(capability, []).append(reason)

    explicit_deep_research = _has(
        lowered,
        r"\bdeep research\b",
        r"\bcomprehensive research\b",
        r"\bin-depth research\b",
        r"\bexhaustive research\b",
        r"\bmulti[- ]facet(?:ed)? research\b",
    )
    if explicit_deep_research:
        add_routed("atlas.deep-research", "explicit_deep_research")

    procurement_text_signal = _has(
        lowered,
        r"\bprocurement\b",
        r"\btender\b",
        r"\bacquisition\b",
        r"\bannual procurement plan\b",
        r"\bapp\b.*\bprocurement\b",
        r"\bbid/no-bid\b",
        r"\bbid no bid\b",
    )
    procurement_signal = bool(collection_set & _PROCUREMENT_PRIMARY_COLLECTION_TYPES) or procurement_text_signal
    if procurement_signal:
        add_routed("atlas.procurement-intelligence", "procurement_semantics")

    economic_policy_signal = _has(
        lowered,
        r"\bbangladesh bank\b",
        r"\bcentral bank\b",
        r"\bmonetary policy\b",
        r"\bfiscal policy\b",
        r"\bforeign exchange policy\b",
        r"\bfx policy\b",
        r"\btrade policy\b",
        r"\beconomic policy\b",
        r"\bexchange control\b",
    )
    if economic_policy_signal:
        add_routed("atlas.economic-policy-intelligence", "economic_policy_semantics")

    contract_subject = _has(
        lowered,
        r"\bcontract\b",
        r"\bagreement\b",
        r"\bclause\b",
    )
    contract_action = _has(
        lowered,
        r"\breview\b",
        r"\banaly[sz](?:e|ing|is)\b",
        r"\bredline(?:s|d)?\b",
        r"\bnegotiat(?:e|ion|ing)\b",
        r"\bpreferred position\b",
        r"\bfallback position\b",
        r"\blegal risk\b",
        r"\bcommercial risk\b",
    )
    if contract_subject and contract_action:
        add_routed("atlas.commercial-contract-review", "commercial_contract_semantics")

    public_equity_research = _has(
        lowered,
        r"\bpublic[- ]equity\b",
        r"\bpublic equities\b",
        r"\bequity investment(?:s)?\b",
        r"\bsecurities research\b",
        r"\bstock research\b",
        r"\bcompare\b.*\bstocks?\b",
    )
    finance_signal = _has(
        lowered,
        r"\bprofit and loss\b",
        r"\bp&l\b",
        r"\bcash flow\b",
        r"\bworking capital\b",
        r"\bgross margin\b",
        r"\bnet margin\b",
        r"\bcommission\b",
        r"\bfx exposure\b",
        r"\breceivables?\b",
        r"\bpayables?\b",
        r"\blanded cost\b",
        r"\bbudget vs actual\b",
        r"\bproject economics\b",
        r"\bpricing\b",
    )
    if finance_signal and not public_equity_research:
        add_routed("atlas.corporate-finance", "corporate_finance_semantics")

    if collection_mode in _ARGUS_MODES:
        specialist.append("argus.collection")
        reasons["argus.collection"] = [f"collection_mode:{collection_mode}"]

    return {
        "kernel": list(KERNEL_CAPABILITIES),
        "routed": routed,
        "specialist": specialist,
        "collection_mode": collection_mode,
        "collection_types": list(collection),
        "task_classes": list(classes),
        "reasons": reasons,
    }


__all__ = ["KERNEL_CAPABILITIES", "plan_canonical_capabilities"]
