from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
import yaml

from atlas_runtime import get_surface_adapter

ROOT = Path(__file__).resolve().parents[2]


class ChatGPTBootstrapIntegrationTests(unittest.TestCase):
    def test_single_file_profile_is_version_bound_and_complete(self) -> None:
        manifest = yaml.safe_load((ROOT / "atlas-os.yaml").read_text(encoding="utf-8"))
        version = manifest["product"]["version"]
        instructions = (
            ROOT / "integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md"
        ).read_text(encoding="utf-8")
        self.assertIn(f"Version: `{version}`", instructions)
        self.assertRegex(instructions, r"Control revision: `atlas-bootstrap-[0-9-]+-r[0-9]+`")
        for required in (
            "ATLAS/chatgpt", "Goal", "Task", "Input", "Processing", "Playbook",
            "Framework", "SOP", "Plan", "Clarification", "Output", "Profile",
            "Library", "Quality", "Blocker", "CAPABILITY_UNAVAILABLE",
            "private chain-of-thought", "international standards",
        ):
            self.assertIn(required, instructions)
        self.assertLess(len(instructions), 8_000)

    def test_profile_and_executable_adapter_share_dashboard_contract(self) -> None:
        dashboard = get_surface_adapter("chatgpt").start_prompt(
            "Verify ChatGPT bootstrap",
            [{"id": "verify", "status": "PENDING", "dependencies": []}],
            plan_id="plan-chatgpt-bootstrap",
            timestamp="2026-10-17T23:54:21+06:00",
            timezone_name="Asia/Dhaka",
        )
        schema = json.loads((ROOT / "schemas/dashboard.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(dashboard, schema, format_checker=jsonschema.FormatChecker())
        self.assertEqual("chatgpt", dashboard["surface"])
        self.assertEqual("verify", dashboard["active_unit"])


if __name__ == "__main__":
    unittest.main()
