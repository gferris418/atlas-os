from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CommandLineTests(unittest.TestCase):
    REQUEST = {
        "objective": "Assess coastal surveillance radar",
        "plan_id": "plan-radar",
        "surface": "chatgpt",
        "timestamp": "2026-10-19T01:00:00+06:00",
        "timezone_name": "Asia/Dhaka",
        "work_units": [
            {"id": "classify", "status": "COMPLETED", "dependencies": []},
            {"id": "assess", "status": "PENDING", "dependencies": ["classify"]},
        ],
    }

    def _run(self, *arguments: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "atlas_runtime", *arguments],
            cwd=ROOT,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_default_text_output_runs_the_public_execution_interface(self) -> None:
        completed = self._run(input_text=json.dumps(self.REQUEST))

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("ATLAS/chatgpt", completed.stdout)
        self.assertIn("State BLOCKED", completed.stdout)
        self.assertIn("MATERIAL_CONTEXT_MATRIX", completed.stdout)
        self.assertIn("Task 1/2", completed.stdout)
        self.assertLessEqual(len(completed.stdout.strip().splitlines()), 4)
        self.assertEqual("", completed.stderr)

    def test_ndjson_output_emits_two_parseable_runtime_events(self) -> None:
        completed = self._run("--format", "ndjson", input_text=json.dumps(self.REQUEST))

        self.assertEqual(0, completed.returncode, completed.stderr)
        events = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(["accepted", "result"], [event["event"] for event in events])
        self.assertEqual("plan-radar", events[0]["plan_id"])
        self.assertEqual("BLOCKED", events[1]["state"])
        self.assertIsNone(events[1]["active_unit"])

    def test_invalid_json_fails_without_a_traceback(self) -> None:
        completed = self._run(input_text="not-json")

        self.assertEqual(2, completed.returncode)
        self.assertIn("invalid JSON input", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertEqual("", completed.stdout)

    def test_invalid_request_matrix_fails_without_a_traceback(self) -> None:
        cases = [
            ((), "[]", "JSON input must be an object"),
            (
                (),
                json.dumps({"objective": "Assess", "work_units": []}),
                "missing required field: plan_id",
            ),
            (("--input", "no-such-execution-request.json"), None, "no-such-execution-request.json"),
        ]
        for arguments, input_text, expected in cases:
            with self.subTest(arguments=arguments, input_text=input_text):
                completed = self._run(*arguments, input_text=input_text)
                self.assertEqual(2, completed.returncode)
                self.assertIn("ATLAS error:", completed.stderr)
                self.assertIn(expected, completed.stderr)
                self.assertNotIn("Traceback", completed.stderr)
                self.assertEqual("", completed.stdout)

    def test_unknown_output_format_uses_argparse_error_boundary(self) -> None:
        completed = self._run("--format", "xml", input_text=json.dumps(self.REQUEST))

        self.assertEqual(2, completed.returncode)
        self.assertIn("invalid choice", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertEqual("", completed.stdout)


if __name__ == "__main__":
    unittest.main()
