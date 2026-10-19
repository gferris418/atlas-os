from __future__ import annotations

import base64
import unittest
from copy import deepcopy

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from atlas_runtime import (
    attest_control_record,
    prepare_execution_lease,
    resolve_trusted_public_key,
    verify_control_record_attestation_with_registry,
    verify_execution_lease,
)


class SigningKeyLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.private_key = Ed25519PrivateKey.generate()
        self.private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.record = {"handoff_id": "HANDOFF-ARGUS-READY", "state": "READY"}

    def _registry(self, *, status: str = "ACTIVE", activated_at: str = "2026-10-01T00:00:00Z", expires_at: str = "2026-12-31T23:59:59Z", record_classes: list[str] | None = None) -> dict:
        return {
            "registry_version": "1.0.0",
            "issuer": "ATLAS_OS",
            "keys": [
                {
                    "key_id": "atlas-primary-2026",
                    "algorithm": "Ed25519",
                    "public_key_base64": base64.b64encode(self.public_bytes).decode("ascii"),
                    "activated_at": activated_at,
                    "expires_at": expires_at,
                    "status": status,
                    "issuer": "ATLAS_OS",
                    "allowed_record_classes": record_classes or ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE"],
                    "supersedes": None,
                }
            ],
        }

    def test_active_key_verifies_for_allowed_record_class(self) -> None:
        registry = self._registry()
        attestation = attest_control_record(
            self.record, key_id="atlas-primary-2026", private_key=self.private_bytes
        )
        self.assertEqual(
            self.public_bytes,
            resolve_trusted_public_key(
                registry,
                key_id="atlas-primary-2026",
                record_class="DOMAIN_CONTEXT_HANDOFF",
                verified_at="2026-10-19T12:00:00Z",
            ),
        )
        self.assertTrue(
            verify_control_record_attestation_with_registry(
                self.record,
                attestation,
                trusted_key_registry=registry,
                record_class="DOMAIN_CONTEXT_HANDOFF",
                verified_at="2026-10-19T12:00:00Z",
            )
        )

    def test_key_lifecycle_fails_closed_before_activation_after_expiry_on_revocation_and_out_of_scope(self) -> None:
        cases = [
            (self._registry(activated_at="2026-10-20T00:00:00Z"), "DOMAIN_CONTEXT_HANDOFF", "2026-10-19T12:00:00Z"),
            (self._registry(expires_at="2026-10-18T23:59:59Z"), "DOMAIN_CONTEXT_HANDOFF", "2026-10-19T12:00:00Z"),
            (self._registry(status="REVOKED"), "DOMAIN_CONTEXT_HANDOFF", "2026-10-19T12:00:00Z"),
            (self._registry(record_classes=["EXECUTION_LEASE"]), "DOMAIN_CONTEXT_HANDOFF", "2026-10-19T12:00:00Z"),
        ]
        for registry, record_class, verified_at in cases:
            with self.subTest(registry=registry), self.assertRaises(ValueError):
                resolve_trusted_public_key(
                    registry,
                    key_id="atlas-primary-2026",
                    record_class=record_class,
                    verified_at=verified_at,
                )

    def test_rotation_overlap_allows_both_active_keys_and_compromise_cutover_revokes_old_key(self) -> None:
        second_private = Ed25519PrivateKey.generate()
        second_public = second_private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        registry = self._registry()
        registry["keys"].append(
            {
                "key_id": "atlas-primary-2026b",
                "algorithm": "Ed25519",
                "public_key_base64": base64.b64encode(second_public).decode("ascii"),
                "activated_at": "2026-10-15T00:00:00Z",
                "expires_at": "2027-01-31T23:59:59Z",
                "status": "ACTIVE",
                "issuer": "ATLAS_OS",
                "allowed_record_classes": ["DOMAIN_CONTEXT_HANDOFF", "EXECUTION_LEASE"],
                "supersedes": "atlas-primary-2026",
            }
        )
        self.assertEqual(
            self.public_bytes,
            resolve_trusted_public_key(registry, key_id="atlas-primary-2026", record_class="EXECUTION_LEASE", verified_at="2026-10-19T12:00:00Z"),
        )
        self.assertEqual(
            second_public,
            resolve_trusted_public_key(registry, key_id="atlas-primary-2026b", record_class="EXECUTION_LEASE", verified_at="2026-10-19T12:00:00Z"),
        )
        compromised = deepcopy(registry)
        compromised["keys"][0]["status"] = "REVOKED"
        with self.assertRaises(ValueError):
            resolve_trusted_public_key(compromised, key_id="atlas-primary-2026", record_class="EXECUTION_LEASE", verified_at="2026-10-19T12:00:00Z")
        self.assertEqual(
            second_public,
            resolve_trusted_public_key(compromised, key_id="atlas-primary-2026b", record_class="EXECUTION_LEASE", verified_at="2026-10-19T12:00:00Z"),
        )


class ExecutionLeaseTests(unittest.TestCase):
    def _handoff(self) -> dict:
        return {
            "contract_version": "1.2.0",
            "handoff_id": "HANDOFF-ARGUS-001",
            "source_task_id": "TASK-SAMPLE-001",
            "source_plan_id": "plan-domain-handoff",
            "source_work_unit_id": "unit-domain-analysis",
            "producer": "ATLAS_OS",
            "consumer": "ARGUS",
            "created_at": "2026-10-18T00:00:00Z",
            "activation_expires_at": "2026-10-19T00:00:00Z",
            "state": "READY",
            "domain_classification": {"status": "CLASSIFIED", "unresolved_facets": [], "risk_flags": []},
            "domain_alignment": {"status": "ALIGNED"},
            "unresolved_material": [],
            "risk_flags": [],
            "payload_sha256": "sha256:" + "a" * 64,
        }

    def test_lease_binds_exact_handoff_and_remains_valid_after_activation_window(self) -> None:
        handoff = self._handoff()
        lease = prepare_execution_lease(
            handoff,
            execution_lease_id="LEASE-ARGUS-001",
            issued_at="2026-10-18T00:05:00Z",
            lease_expires_at="2026-10-22T00:05:00Z",
        )
        self.assertEqual("1.0.0", lease["contract_version"])
        self.assertEqual(handoff["handoff_id"], lease["handoff_id"])
        self.assertEqual(handoff["payload_sha256"], lease["handoff_payload_sha256"])
        self.assertTrue(
            verify_execution_lease(
                lease,
                handoff,
                verified_at="2026-10-21T12:00:00Z",
                expected_lease_id="LEASE-ARGUS-001",
            )
        )

    def test_expired_cross_execution_and_superseded_lease_fail_closed(self) -> None:
        handoff = self._handoff()
        lease = prepare_execution_lease(
            handoff,
            execution_lease_id="LEASE-ARGUS-001",
            issued_at="2026-10-18T00:05:00Z",
            lease_expires_at="2026-10-20T00:05:00Z",
        )
        with self.assertRaises(ValueError):
            verify_execution_lease(lease, handoff, verified_at="2026-10-20T00:05:01Z")
        changed_handoff = deepcopy(handoff)
        changed_handoff["handoff_id"] = "HANDOFF-ARGUS-OTHER"
        with self.assertRaises(ValueError):
            verify_execution_lease(lease, changed_handoff, verified_at="2026-10-19T00:00:00Z")
        renewed = prepare_execution_lease(
            handoff,
            execution_lease_id="LEASE-ARGUS-002",
            issued_at="2026-10-19T23:00:00Z",
            lease_expires_at="2026-10-24T23:00:00Z",
            supersedes_lease_id="LEASE-ARGUS-001",
        )
        self.assertTrue(verify_execution_lease(renewed, handoff, verified_at="2026-10-21T00:00:00Z", expected_lease_id="LEASE-ARGUS-002"))
        with self.assertRaises(ValueError):
            verify_execution_lease(lease, handoff, verified_at="2026-10-19T12:00:00Z", expected_lease_id="LEASE-ARGUS-002")


if __name__ == "__main__":
    unittest.main()
