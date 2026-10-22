from __future__ import annotations

from .models import ExecutionResult

_STAGE_PROGRESS: dict[str, int] = {
    "MISSION_CONTROL": 5,
    "UNDERSTAND_AND_NORMALIZE": 15,
    "MINIMAL_DOMAIN_FRAMING": 25,
    "ROUTE": 35,
    "APPROVAL": 35,
    "EXECUTION": 60,
    "QUALITY_GATE": 80,
    "FINAL_VERIFY": 90,
    "PERSISTENCE": 95,
    "COMPLETE": 100,
}


def progress_for_stage(stage: str) -> int:
    try:
        return _STAGE_PROGRESS[stage]
    except KeyError as exc:
        raise ValueError(f"unknown ATLAS stage: {stage}") from exc


def _progress_bar(percent: int, width: int = 10) -> str:
    filled = min(width, max(0, round(percent * width / 100)))
    return "█" * filled + "░" * (width - filled)


def _mission_control_state(stage: str) -> str:
    if stage == "EXECUTION":
        return "EXECUTE"
    if stage == "FINAL_VERIFY":
        return "VERIFY"
    return stage


def render_fast_text(result: ExecutionResult) -> str:
    """Render compact user-facing status without altering execution semantics."""
    dashboard = result.dashboard
    stage = str(dashboard["active_stage"])
    progress = progress_for_stage(stage)
    blocker = dashboard.get("blocker_or_approval") or "NONE"
    control_plane = dashboard.get("route") or result.route.mechanism
    first = (
        f"ATLAS [{_progress_bar(progress)}] {progress}% | "
        f"MC: {_mission_control_state(stage)} | CP: {control_plane} | "
        f"STATUS: {result.state} | BLOCKER: {blocker}"
    )
    second = f"NEXT: {dashboard['next_action']}"
    return f"{first}\n{second}"
