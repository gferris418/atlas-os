"""Validation shared by every AI-host surface boundary."""

from __future__ import annotations

import re

_SURFACE_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_MAX_SURFACE_ID_LENGTH = 64


def validate_surface_id(surface_id: str) -> str:
    """Return a safe provider-neutral AI-host identifier.

    Surface identifiers are open-ended so a new agent host does not require an
    ATLAS runtime release. Validation keeps the value safe for dashboards,
    records, and adapter lookup.
    """

    if (
        not isinstance(surface_id, str)
        or len(surface_id) > _MAX_SURFACE_ID_LENGTH
        or _SURFACE_ID.fullmatch(surface_id) is None
    ):
        raise ValueError(
            "surface identifier must be a lowercase AI-host slug of 1-64 characters"
        )
    return surface_id


__all__ = ["validate_surface_id"]
