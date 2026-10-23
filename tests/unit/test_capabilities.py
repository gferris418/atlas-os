from __future__ import annotations

import unittest

from atlas_runtime.capabilities import (
    CapabilityError,
    CapabilityReplayError,
    InMemoryReplayGuard,
    issue_remote_capability,
    verify_remote_capability,
)


SECRET = b"0123456789abcdef0123456789abcdef"


class RecordingReplayGuard:
    def __init__(self) -> None:
        self.seen: set[str] = set()

    def consume(self, jti: str, exp: int, now: int) -> bool:
        del exp, now
        if jti in self.seen:
            return False
        self.seen.add(jti)
        return True


class CapabilityV2Tests(unittest.TestCase):
    def test_round_trip_is_task_and_intent_bound(self) -> None:
        token = issue_remote_capability(
            SECRET,
            task_id="ATLAS-123",
            intent="Build a dossier on ST Engineering.",
            key_id="test-key",
            now=1_800_000_000,
            ttl_seconds=120,
            nonce="nonce-1",
        )
        claims = verify_remote_capability(
            token,
            lambda key_id: SECRET if key_id == "test-key" else None,
            task_id="ATLAS-123",
            intent="Build a dossier on ST Engineering.",
            replay_guard=InMemoryReplayGuard(),
            now=1_800_000_060,
        )
        self.assertEqual("ATLAS", claims["iss"])
        self.assertEqual("argus", claims["sub"])
        self.assertEqual("ARGUS", claims["aud"])
        self.assertEqual("intelligence_collection", claims["capability"])
        self.assertEqual("intelligence_collection:execute", claims["scope"])
        self.assertEqual("nonce-1", claims["jti"])

    def test_replay_guard_is_an_interface_not_a_concrete_class(self) -> None:
        guard = RecordingReplayGuard()
        token = issue_remote_capability(
            SECRET,
            task_id="ATLAS-123",
            intent="Collect intelligence.",
            key_id="test-key",
            now=1_800_000_000,
            nonce="nonce-interface",
        )
        claims = verify_remote_capability(
            token,
            lambda _key_id: SECRET,
            task_id="ATLAS-123",
            intent="Collect intelligence.",
            replay_guard=guard,
            now=1_800_000_030,
        )
        self.assertEqual("nonce-interface", claims["jti"])

    def test_replay_is_rejected(self) -> None:
        guard = InMemoryReplayGuard()
        token = issue_remote_capability(
            SECRET,
            task_id="ATLAS-123",
            intent="Collect intelligence.",
            key_id="test-key",
            now=1_800_000_000,
            nonce="nonce-2",
        )
        kwargs = {
            "task_id": "ATLAS-123",
            "intent": "Collect intelligence.",
            "replay_guard": guard,
            "now": 1_800_000_030,
        }
        verify_remote_capability(token, lambda _key_id: SECRET, **kwargs)
        with self.assertRaises(CapabilityReplayError):
            verify_remote_capability(token, lambda _key_id: SECRET, **kwargs)

    def test_expired_wrong_task_and_wrong_intent_are_rejected(self) -> None:
        token = issue_remote_capability(
            SECRET,
            task_id="ATLAS-123",
            intent="Collect intelligence.",
            key_id="test-key",
            now=1_800_000_000,
            ttl_seconds=60,
            nonce="nonce-3",
        )

        def resolver(_key_id: str) -> bytes:
            return SECRET

        with self.assertRaises(CapabilityError):
            verify_remote_capability(
                token,
                resolver,
                task_id="ATLAS-123",
                intent="Collect intelligence.",
                replay_guard=InMemoryReplayGuard(),
                now=1_800_000_061,
            )
        with self.assertRaises(CapabilityError):
            verify_remote_capability(
                token,
                resolver,
                task_id="ATLAS-999",
                intent="Collect intelligence.",
                replay_guard=InMemoryReplayGuard(),
                now=1_800_000_030,
            )
        with self.assertRaises(CapabilityError):
            verify_remote_capability(
                token,
                resolver,
                task_id="ATLAS-123",
                intent="Different intent.",
                replay_guard=InMemoryReplayGuard(),
                now=1_800_000_030,
            )

    def test_ttl_is_capped_by_contract(self) -> None:
        with self.assertRaises(CapabilityError):
            issue_remote_capability(
                SECRET,
                task_id="ATLAS-123",
                intent="Collect intelligence.",
                key_id="test-key",
                now=1_800_000_000,
                ttl_seconds=301,
            )


if __name__ == "__main__":
    unittest.main()
