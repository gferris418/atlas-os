from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class ExternalProofEvidenceTests(unittest.TestCase):
    def _valid_codex_evidence(self) -> dict:
        session_id = "codex-session-rc6-001"
        timestamp = "2026-10-22T07:45:00+06:00"
        source_commit = "aafa1194383d4739f6ed2e34000579551a2cd44b"
        common = {"session_id": session_id, "timestamp": timestamp}
        return {
            "schema": "schemas/external-proof-evidence.schema.json",
            "id": "external-proof.codex.rc6.001",
            "verification_id": "verification.codex",
            "surface": "codex",
            "session_id": session_id,
            "timestamp": timestamp,
            "timezone": "Asia/Dhaka",
            "source_commit": source_commit,
            "product_version": "2.0.2-rc.6",
            "control_revision": "atlas-bootstrap-2026-10-22-r10",
            "resolved_authority": "atlas-os.yaml",
            "fresh_session": True,
            "independent": True,
            "reviewer": "independent-codex-verifier",
            "checks": [
                {
                    "check_id": "CHK-01",
                    "result": "PASS",
                    "evidence": {
                        **common,
                        "source_commit": source_commit,
                        "resolved_authority": "atlas-os.yaml",
                    },
                    "observed": {
                        "product_version": "2.0.2-rc.6",
                        "control_revision": "atlas-bootstrap-2026-10-22-r10",
                        "product_authority": "atlas-os.yaml",
                    },
                },
                {
                    "check_id": "CHK-02",
                    "result": "PASS",
                    "evidence": {
                        **common,
                        "source_commit": source_commit,
                        "command": "python -m atlas_runtime --input examples/execution-request.json",
                        "exit_status": 0,
                        "stdout": "Plan plan-example READY",
                    },
                    "observed": {"exit_status": 0, "plan_id": "plan-example"},
                },
                {
                    "check_id": "CHK-03",
                    "result": "PASS",
                    "evidence": {**common, "response": "ATLAS_DIRECT economic-policy result"},
                    "observed": {
                        "collection_mode": "ATLAS_DIRECT",
                        "capability_plan": ["atlas.economic-policy-intelligence"],
                    },
                },
                {
                    "check_id": "CHK-04",
                    "result": "PASS",
                    "evidence": {**common, "response": "ARGUS collection result"},
                    "observed": {
                        "collection_mode": "ARGUS_COLLECTION",
                        "specialist": "ARGUS",
                        "capability_plan": ["argus.collection"],
                    },
                },
                {
                    "check_id": "CHK-05",
                    "result": "PASS",
                    "evidence": {**common, "response": "Procurement collection result"},
                    "observed": {
                        "collection_mode": "ARGUS_COLLECTION",
                        "collection_type": ["PROCUREMENT_PLAN"],
                        "capability_plan": ["atlas.procurement-intelligence", "argus.collection"],
                    },
                },
                {
                    "check_id": "CHK-06",
                    "result": "PASS",
                    "evidence": {**common, "response": "Contract review result"},
                    "observed": {
                        "collection_mode": "NONE",
                        "capability_plan": ["atlas.commercial-contract-review"],
                    },
                },
                {
                    "check_id": "CHK-07",
                    "result": "PASS",
                    "evidence": {**common, "response": "Hybrid comparison result"},
                    "observed": {
                        "collection_mode": "HYBRID",
                        "final_analysis_owner": "ATLAS",
                    },
                },
            ],
            "overall_result": "PASS",
            "limitations": "",
        }

    def _run_validator(self, record: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "evidence.yaml"
            path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    "tools/validate/validate_external_evidence.py",
                    ".",
                    path.as_posix(),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_valid_codex_evidence_satisfies_release_contract(self) -> None:
        completed = self._run_validator(self._valid_codex_evidence())
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("external proof evidence valid", completed.stdout.lower())

    def test_nonfresh_evidence_fails_closed(self) -> None:
        record = self._valid_codex_evidence()
        record["fresh_session"] = False
        completed = self._run_validator(record)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("fresh_session", completed.stdout + completed.stderr)

    def test_missing_required_check_evidence_fails_closed(self) -> None:
        record = self._valid_codex_evidence()
        del record["checks"][1]["evidence"]["stdout"]
        completed = self._run_validator(record)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("stdout", completed.stdout + completed.stderr)

    def test_false_assertion_cannot_be_recorded_as_pass(self) -> None:
        record = self._valid_codex_evidence()
        record["checks"][3]["observed"]["collection_mode"] = "ATLAS_DIRECT"
        completed = self._run_validator(record)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("CHK-04", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
