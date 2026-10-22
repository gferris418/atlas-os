from __future__ import annotations

from typing import Final

QUALITY_TIERS: Final[tuple[str, ...]] = ("Q0", "Q1", "Q2", "Q3", "Q4", "Q5")

QUALITY_REQUIREMENTS: Final[dict[str, tuple[str, ...]]] = {
    "Q0": ("deterministic_correctness",),
    "Q1": ("authoritative_source", "claim_traceability"),
    "Q2": ("relevant_evidence", "basic_reconciliation", "claim_traceability"),
    "Q3": (
        "authoritative_source_priority",
        "corroboration",
        "source_diversity",
        "contradiction_analysis",
        "claim_traceability",
    ),
    "Q4": (
        "authoritative_source_priority",
        "broad_multi_angle_evidence",
        "corroboration",
        "source_diversity",
        "entity_resolution",
        "contradiction_analysis",
        "competing_hypotheses",
        "material_gap_disclosure",
        "confidence_calibration",
        "claim_traceability",
        "decision_objective_coverage",
    ),
    "Q5": (
        "authoritative_source_priority",
        "maximum_assurance_corroboration",
        "high_source_diversity",
        "entity_resolution",
        "contradiction_analysis",
        "adverse_case_testing",
        "competing_hypotheses",
        "material_gap_disclosure",
        "confidence_calibration",
        "claim_traceability",
        "decision_objective_coverage",
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


def determine_required_quality_tier(objective: str, requested_floor: str | None = None) -> str:
    """Return the minimum assurance tier required by the objective.

    This policy is intentionally deterministic. A requested floor may raise the
    automatic tier but can never lower it.
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

    if requested_floor is None:
        return automatic
    quality_rank(requested_floor)
    return max_quality_tier(automatic, requested_floor)
