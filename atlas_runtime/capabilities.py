from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from collections.abc import Callable
from threading import Lock
from typing import Any, Protocol

from .contract import EXECUTION_CONTRACT


class CapabilityError(ValueError):
    pass


class CapabilityReplayError(CapabilityError):
    pass


class ReplayGuard(Protocol):
    def consume(self, jti: str, exp: int, now: int) -> bool: ...


class InMemoryReplayGuard:
    """Process-local replay protection for tests and single-process deployments.

    Distributed remote deployments should provide a shared replay guard implementing
    the same consume(jti, exp, now) interface.
    """

    def __init__(self) -> None:
        self._seen: dict[str, int] = {}
        self._lock = Lock()

    def consume(self, jti: str, exp: int, now: int) -> bool:
        with self._lock:
            expired = [key for key, deadline in self._seen.items() if deadline < now]
            for key in expired:
                del self._seen[key]
            if jti in self._seen:
                return False
            self._seen[jti] = exp
            return True


def _policy() -> dict[str, Any]:
    return dict(EXECUTION_CONTRACT["remote_capability"])


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode((value + padding).encode("ascii"))
    except Exception as exc:
        raise CapabilityError("invalid capability encoding") from exc


def _json_segment(value: dict[str, Any]) -> str:
    return _b64url_encode(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _intent_hash(intent: str) -> str:
    if not isinstance(intent, str) or not intent.strip():
        raise CapabilityError("intent must be a non-empty string")
    return hashlib.sha256(intent.encode("utf-8")).hexdigest()


def _validate_secret(secret: bytes) -> bytes:
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise CapabilityError("capability secret must be at least 32 bytes")
    return secret


def issue_remote_capability(
    secret: bytes,
    *,
    task_id: str,
    intent: str,
    key_id: str,
    now: int,
    ttl_seconds: int = 120,
    nonce: str | None = None,
) -> str:
    secret = _validate_secret(secret)
    policy = _policy()
    max_ttl = int(policy["max_ttl_seconds"])
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or ttl_seconds < 1 or ttl_seconds > max_ttl:
        raise CapabilityError(f"ttl_seconds must be between 1 and {max_ttl}")
    if isinstance(now, bool) or not isinstance(now, int) or now < 0:
        raise CapabilityError("now must be a non-negative integer timestamp")
    if not isinstance(task_id, str) or not task_id.strip():
        raise CapabilityError("task_id must be a non-empty string")
    if not isinstance(key_id, str) or not key_id.strip():
        raise CapabilityError("key_id must be a non-empty string")
    jti = nonce or secrets.token_urlsafe(18)
    if not isinstance(jti, str) or not jti.strip():
        raise CapabilityError("nonce must be a non-empty string")

    header = {"alg": policy["algorithm"], "kid": key_id, "typ": "ATLAS-CAP"}
    claims = {
        "v": policy["version"],
        "iss": policy["issuer"],
        "sub": policy["subject"],
        "aud": policy["audience"],
        "capability": policy["capability"],
        "scope": policy["scope"],
        "task_id": task_id,
        "intent_hash": _intent_hash(intent),
        "iat": now,
        "exp": now + ttl_seconds,
        "jti": jti,
    }
    encoded_header = _json_segment(header)
    encoded_claims = _json_segment(claims)
    signing_input = f"{encoded_header}.{encoded_claims}".encode("ascii")
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_claims}.{_b64url_encode(signature)}"


def verify_remote_capability(
    token: str,
    secret_resolver: Callable[[str], bytes | None],
    *,
    task_id: str,
    intent: str,
    replay_guard: ReplayGuard,
    now: int,
) -> dict[str, Any]:
    if not isinstance(token, str):
        raise CapabilityError("capability must be a string")
    parts = token.split(".")
    if len(parts) != 3:
        raise CapabilityError("capability must have exactly three segments")
    if not callable(secret_resolver):
        raise CapabilityError("secret_resolver must be callable")
    if not callable(getattr(replay_guard, "consume", None)):
        raise CapabilityError("replay_guard must provide consume(jti, exp, now)")
    if isinstance(now, bool) or not isinstance(now, int) or now < 0:
        raise CapabilityError("now must be a non-negative integer timestamp")

    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
        claims = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapabilityError("capability contains invalid JSON") from exc
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise CapabilityError("capability segments must decode to objects")

    policy = _policy()
    if header.get("alg") != policy["algorithm"] or header.get("typ") != "ATLAS-CAP":
        raise CapabilityError("unsupported capability header")
    key_id = header.get("kid")
    if not isinstance(key_id, str) or not key_id:
        raise CapabilityError("capability key id is required")
    secret = secret_resolver(key_id)
    if secret is None:
        raise CapabilityError("unknown capability key id")
    secret = _validate_secret(secret)

    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    expected = hmac.new(secret, signing_input, hashlib.sha256).digest()
    supplied = _b64url_decode(parts[2])
    if not hmac.compare_digest(expected, supplied):
        raise CapabilityError("capability signature mismatch")

    required = {
        "v", "iss", "sub", "aud", "capability", "scope", "task_id",
        "intent_hash", "iat", "exp", "jti",
    }
    if not required.issubset(claims):
        raise CapabilityError("capability is missing required claims")
    if claims["v"] != policy["version"]:
        raise CapabilityError("unsupported capability version")
    if claims["iss"] != policy["issuer"] or claims["aud"] != policy["audience"]:
        raise CapabilityError("capability issuer or audience mismatch")
    if claims["sub"] != policy["subject"] or claims["capability"] != policy["capability"]:
        raise CapabilityError("capability subject or capability mismatch")
    if claims["scope"] != policy["scope"]:
        raise CapabilityError("capability scope mismatch")
    if claims["task_id"] != task_id:
        raise CapabilityError("capability task mismatch")
    if claims["intent_hash"] != _intent_hash(intent):
        raise CapabilityError("capability intent mismatch")

    issued_at = claims["iat"]
    expires_at = claims["exp"]
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (issued_at, expires_at)):
        raise CapabilityError("capability timestamps must be integers")
    max_ttl = int(policy["max_ttl_seconds"])
    if expires_at <= issued_at or expires_at - issued_at > max_ttl:
        raise CapabilityError("capability lifetime exceeds policy")
    max_skew = int(policy["max_clock_skew_seconds"])
    if now < issued_at - max_skew:
        raise CapabilityError("capability is not yet valid")
    if now > expires_at:
        raise CapabilityError("capability has expired")

    jti = claims["jti"]
    if not isinstance(jti, str) or not jti:
        raise CapabilityError("capability jti is required")
    if not replay_guard.consume(jti, expires_at, now):
        raise CapabilityReplayError("capability replay detected")
    return dict(claims)


__all__ = [
    "CapabilityError",
    "CapabilityReplayError",
    "InMemoryReplayGuard",
    "ReplayGuard",
    "issue_remote_capability",
    "verify_remote_capability",
]
