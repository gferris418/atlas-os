from __future__ import annotations

import unittest
from copy import deepcopy

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from atlas_runtime import attest_control_record, verify_control_record_attestation


class ControlAttestationTests(unittest.TestCase):
    def setUp(self) -> None:
        private_key = Ed25519PrivateKey.generate()
        self.private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.record = {"handoff_id": "HANDOFF-ARGUS-READY", "state": "READY"}

    def test_atlas_attestation_verifies_with_pinned_public_key(self) -> None:
        attestation = attest_control_record(
            self.record, key_id="atlas-test-2026", private_key=self.private_bytes
        )
        self.assertTrue(verify_control_record_attestation(
            self.record,
            attestation,
            trusted_public_keys={"atlas-test-2026": self.public_bytes},
        ))

    def test_changed_record_unknown_key_and_changed_signature_fail_closed(self) -> None:
        attestation = attest_control_record(
            self.record, key_id="atlas-test-2026", private_key=self.private_bytes
        )
        cases = []
        changed_record = deepcopy(self.record)
        changed_record["state"] = "BLOCKED"
        cases.append((changed_record, attestation, {"atlas-test-2026": self.public_bytes}))
        cases.append((self.record, attestation, {}))
        changed_attestation = deepcopy(attestation)
        changed_attestation["signature"] = "AAAA"
        cases.append((self.record, changed_attestation, {"atlas-test-2026": self.public_bytes}))
        for record, candidate, keys in cases:
            with self.subTest(record=record, keys=keys), self.assertRaises(ValueError):
                verify_control_record_attestation(
                    record, candidate, trusted_public_keys=keys
                )


if __name__ == "__main__":
    unittest.main()
