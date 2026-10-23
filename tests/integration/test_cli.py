from __future__ import annotations

import io
import json
import unittest

from atlas_runtime.cli import main


class CliTests(unittest.TestCase):
    def test_json_output_exposes_clean_route_contract(self) -> None:
        stdin = io.StringIO(json.dumps({"objective": "Find the current Bangladesh Railway tenders.", "host": "chatgpt"}))
        stdout = io.StringIO()
        stderr = io.StringIO()
        code = main(["--format", "json"], stdin=stdin, stdout=stdout, stderr=stderr)
        self.assertEqual(0, code, stderr.getvalue())
        payload = json.loads(stdout.getvalue())
        self.assertEqual("DIRECT_SEARCH", payload["route"]["mechanism"])
        self.assertEqual("ATLAS", payload["next_step_authority"])
        self.assertEqual(
            ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            payload["pre_execution_flow"],
        )

    def test_missing_objective_fails_cleanly(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        code = main(["--format", "json"], stdin=io.StringIO("{}"), stdout=stdout, stderr=stderr)
        self.assertEqual(2, code)
        self.assertIn("missing required field: objective", stderr.getvalue())

    def test_malformed_optional_fields_fail_cleanly(self) -> None:
        invalid_payloads = (
            {"objective": "Build a dossier.", "approvals": None},
            {"objective": "Build a dossier.", "approvals": "ARGUS_ACTIVATION"},
            {"objective": "Build a dossier.", "context": []},
            {"objective": "Build a dossier.", "provider_result": "returned"},
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                stdout = io.StringIO()
                stderr = io.StringIO()
                code = main(
                    ["--format", "json"],
                    stdin=io.StringIO(json.dumps(payload)),
                    stdout=stdout,
                    stderr=stderr,
                )
                self.assertEqual(2, code)
                self.assertEqual("", stdout.getvalue())
                self.assertIn("ATLAS error:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
