from __future__ import annotations

import unittest
from pathlib import Path

from tools.plugin_release_gate import load_canonical_argus_contract


ROOT = Path(__file__).resolve().parents[2]


class ReleaseContractSourceTests(unittest.TestCase):
    def test_release_gate_reads_required_invariants_from_canonical_contract(self) -> None:
        required = load_canonical_argus_contract(ROOT)
        self.assertEqual("MISSION_CONTROL_FIRST", required["prompt_entry"])
        self.assertEqual("every_user_prompt_while_atlas_active", required["prompt_entry_scope"])
        self.assertEqual("intelligence_collection", required["capability"])
        self.assertEqual("argus", required["provider"])
        self.assertEqual("ARGUS_ACTIVATION", required["approval_key"])
        self.assertEqual("ATLAS", required["activation_authority"])
        self.assertEqual("ATLAS", required["next_step_authority"])
        self.assertEqual("ATLAS", required["provider_return_target"])
        self.assertTrue(required["explicit_user_approval_required"])
        self.assertEqual(
            ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            required["pre_execution_flow"],
        )


if __name__ == "__main__":
    unittest.main()
