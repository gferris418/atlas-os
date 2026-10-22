from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

_CHAT_ROOT = "General/Business Intelligence/30_OPERATIONS/CHAT_LOGS"
_SAFE_ID = re.compile(r"[^A-Za-z0-9._-]+")
_ALLOWED_METADATA = (
    "task_id",
    "conversation_id_source",
    "route",
    "required_quality_tier",
    "achieved_quality_tier",
    "quality_gate",
    "providers",
    "completion_status",
    "atlas_version",
    "atlas_commit",
    "argus_version",
    "argus_commit",
    "pointers",
    "mission_control_state",
    "control_plane",
)


def _safe_identifier(value: str) -> str:
    cleaned = _SAFE_ID.sub("-", value.strip()).strip("-")
    if not cleaned:
        raise ValueError("identifier must contain at least one safe character")
    return cleaned


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chat_event_path(*, conversation_id: str, turn_id: str, timestamp_utc: str) -> str:
    if len(timestamp_utc) < 7 or timestamp_utc[4] != "-":
        raise ValueError("timestamp_utc must begin with YYYY-MM")
    month = timestamp_utc[:7]
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("timestamp_utc must begin with YYYY-MM")
    conversation = _safe_identifier(conversation_id)
    turn = _safe_identifier(turn_id)
    return f"{_CHAT_ROOT}/{month}/CHAT_{conversation}_T{turn}.md"


def _frontmatter_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (list, tuple)):
        return json.dumps(list(value), ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9._/-]+", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def build_chat_event_markdown(
    *,
    visible_prompt: str,
    visible_response: str,
    conversation_id: str,
    turn_id: str,
    timestamp_utc: str,
    metadata: Mapping[str, Any] | None = None,
) -> str:
    """Serialize one immutable completed-turn audit event.

    The API intentionally accepts only user-visible prompt/response content plus
    allowlisted execution metadata. Hidden reasoning, system/developer text,
    credentials, signed URLs, and raw tool payloads have no persistence field.
    """
    prompt_hash = _sha256(visible_prompt)
    response_hash = _sha256(visible_response)
    event_material = f"{conversation_id}\0{turn_id}\0{response_hash}"
    event_id = hashlib.sha256(event_material.encode("utf-8")).hexdigest()
    supplied = metadata or {}

    fields: list[tuple[str, Any]] = [
        ("event_type", "ATLAS_CHAT_TURN"),
        ("event_id", event_id),
        ("conversation_id", conversation_id),
        ("turn_id", turn_id),
        ("timestamp_utc", timestamp_utc),
        ("prompt_sha256", prompt_hash),
        ("response_sha256", response_hash),
    ]
    for key in _ALLOWED_METADATA:
        if key in supplied:
            fields.append((key, supplied[key]))

    frontmatter = ["---"]
    frontmatter.extend(f"{key}: {_frontmatter_value(value)}" for key, value in fields)
    frontmatter.append("---")

    return "\n".join(
        [
            *frontmatter,
            "",
            "# User-visible prompt",
            "",
            visible_prompt,
            "",
            "# User-visible response",
            "",
            visible_response,
            "",
        ]
    )
