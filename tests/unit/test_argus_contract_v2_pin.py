from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARGUS_COMMIT = "0a78e94b1dd2d6d2783a1d1145a70217b022b79b"


class ArgusContractV2PinTests(unittest.TestCase):
    def test_release_policy_pins_verified_argus_contract_v2(self) -> None:
        policy = yaml.safe_load((ROOT / ".github" / "plugin-release-policy.yaml").read_text(encoding="utf-8"))
        compatibility = policy["argus_compatibility"]
        self.assertEqual(ARGUS_COMMIT, compatibility["compatible_commit"])
        self.assertEqual("2.0.0", compatibility["contract_version"])


if __name__ == "__main__":
    unittest.main()
