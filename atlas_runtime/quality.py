from __future__ import annotations

from typing import Any, Final, Mapping

QUALITY_TIERS: Final[tuple[str, ...]] = ("Q0", "Q1", "Q2", "Q3", "Q4", "Q5")

QUALITY_REQUIREMENTS: Final[dict[str, tuple[str, ...]]] = {
    "Q0": ("deterministic_correctness",),
    "Q1": ("authoritative_source", "claim_traceability"),
    "Q2": ("relevant_evidence", "basic_reconciliation", "claim_traceability"),
    "Q3": (
        "relevant_evidence",
        "basic_reconciliation",
        "authoritative_source_priority",
        "corroboration",
        "source_diversity",
        "contradiction_analysis",
        "claim_traceability",
    ),
    "Q4": (
        "relevant_evidence",
        "basic_reconciliation",
        "authoritative_source_priority",
        "corroboration",
        "source_diversity",
        "contradiction_analysis",
        "claim_traceability",
        "broad_multi_angle_evidence",
        "entity_resolution",
        "competing_hypotheses",
        "material_gap_disclosure",
        "confidence_calibration",
        "decision_objective_coverage",
    ),
    "Q5": (
        "relevant_evidence",
        "basic_reconciliation",
        "authoritative_source_priority",
        "corroboration",
        "source_diversity",
        "contradiction_analysis",
        "claim_traceability",
        "broad_multi_angle_evidence",
        "entity_resolution",
        "competing_hypotheses",
        "material_gap_disclosure",
        "confidence_calibration",
        "decision_objective_coverage",
        "maximum_assurance_corroboration",
        "high_source_diversity",
        "adverse_case_testing",
        "explicit_stopping_justification",
    ),
}


def quality_rank(tier: str) -> int:
    try:
        return QUALITY_TIERS.index(tier)
    except ValueError as exc:
        raise ValueError(f"unknown quality tier: {tier}") from exc


def max_quality_tier(*tiers: str) -> str:
    return max(tiers, key=quality_rank)


def quality_requirements(tier: str) -> tuple[str, ...]:
    quality_rank(tier)
    return QUALITY_REQUIREMENTS[tier]


def _contextual_quality_floor(quality_context: Mapping[str, Any] | None) -> str | None:
    if not quality_context:
        return None

    consequence = str(quality_context.get("decision_consequence", "")).strip().lower()
    importance = str(quality_context.get("decision_importance", "")).strip().lower()
    reversibility = str(quality_context.get("reversibility", "")).strip().lower()
    uncertainty = str(quality_context.get("uncertainty", "")).strip().lower()
    evidence_condition = str(quality_context.get("evidence_condition", "")).strip().lower()
    risk_level = str(quality_context.get("risk_level", "")).strip().lower()
    risk_flags_raw = quality_context.get("risk_flags", ())
    risk_flags = (
        tuple(flag for flag in risk_flags_raw if isinstance(flag, str) and flag.strip())
        if isinstance(risk_flags_raw, (list, tuple, set, frozenset))
        else ()
    )

    if (
        reversibility in {"irreversible", "effectively_irreversible"}
        or consequence in {"critical", "catastrophic"}
        or importance == "critical"
        or risk_level == "critical"
    ):
        return "Q5"
    if consequence == "high" or importance == "high":
        return "Q4"
    if (
        uncertainty == "high"
        or evidence_condition in {"conflicted", "disputed", "stale", "incomplete", "fragmented"}
        or risk_level == "high"
        or bool(risk_flags)
    ):
        return "Q3"
    return None


def determine_required_quality_tier(
    objective: str,
    requested_floor: str | None = None,
    quality_context: Mapping[str, Any] | None = None,
) -> str:
    """Return the minimum assurance tier required by the objective and context.

    The policy is deterministic. Context may raise the automatically inferred
    tier based on decision consequence, reversibility, uncertainty, evidence
    condition, or risk. An explicit requested floor may raise the result again,
    but neither context nor a requested floor can lower the required tier.
    """
    text = " ".join(objective.lower().split())

    q5_signals = (
        "maximum-assurance",
        "maximum assurance",
        "critical board decision",
        "irreversible high-value",
        "irreversible high value",
        "mission-critical decision",
        "mission critical decision",
    )
    if any(signal in text for signal in q5_signals):
        automatic = "Q5"
    elif (
        any(signal in text for signal in ("should ", "which oem", "which supplier", "which partner", "strategic decision", "decision-grade"))
        and any(
            signal in text
            for signal in (
                "pursue",
                "programme",
                "program",
                "opportunity",
                "approach",
                "select",
                "choose",
                "supplier",
                "oem",
                "partner",
            )
        )
    ):
        automatic = "Q4"
    elif (
        any(signal in text for signal in ("investigate", "due diligence", "high assurance", "high-assurance"))
        and any(signal in text for signal in ("verify", "authoritative", "corroborat", "claims", "evidence"))
    ):
        automatic = "Q3"
    elif any(signal in text for signal in ("explain", "analyze", "analyse", "compare", "implication", "assessment")):
        automatic = "Q2"
    elif any(
        signal in text
        for signal in (
            "closing date",
            "deadline",
            "current price",
            "latest price",
            "official date",
            "lookup",
            "look up",
            "what is the date",
        )
    ):
        automatic = "Q1"
    elif any(signal in text for signal in ("calculate", "convert", "sum ", "difference", "percentage", "format ", "transform ")):
        automatic = "Q0"
    else:
        automatic = "Q2"

    contextual_floor = _contextual_quality_floor(quality_context)
    if contextual_floor is not None:
        automatic = max_quality_tier(automatic, contextual_floor)

    if requested_floor is None:
        return automatic
    quality_rank(requested_floor)
    return max_quality_tier(automatic, requested_floor)


def evaluate_quality_gate(required_tier: str, ledger: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether provider evidence satisfies the required assurance tier."""
    quality_rank(required_tier)
    achieved_tier = ledger.get("achieved_tier")
    if not isinstance(achieved_tier, str):
        achieved_tier = "Q0"
    quality_rank(achieved_tier)

    passed_raw = ledger.get("passed_requirements", ())
    passed_requirements = {
        item for item in passed_raw if isinstance(item, str)
    } if isinstance(passed_raw, (list, tuple, set, frozenset)) else set()

    blocking_reasons: list[str] = []
    if quality_rank(achieved_tier) < quality_rank(required_tier):
        blocking_reasons.append("achieved_quality_below_required")

    for requirement in quality_requirements(required_tier):
        if requirement not in passed_requirements:
            blocking_reasons.append(f"missing_requirement:{requirement}")

    gaps_raw = ledger.get("irreducible_gaps", ())
    irreducible_gaps = [
        item for item in gaps_raw if isinstance(item, str) and item.strip()
    ] if isinstance(gaps_raw, (list, tuple)) else []

    if not blocking_reasons:
        status = "PASS"
    elif irreducible_gaps:
        status = "IRREDUCIBLE_GAP"
    else:
        status = "CONTINUE"

    return {
        "status": status,
        "required_tier": required_tier,
        "achieved_tier": achieved_tier,
        "blocking_reasons": blocking_reasons,
        "irreducible_gaps": irreducible_gaps,
        "evidence_confidence": ledger.get("evidence_confidence"),
    }
