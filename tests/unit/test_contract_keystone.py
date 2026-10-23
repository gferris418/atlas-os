from __future__ import annotations

import unittest

from atlas_runtime.contract import ARGUS_APPROVAL, EXECUTION_CONTRACT, PRE_EXECUTION_FLOW


class ContractKeystoneTests(unittest.TestCase):
    def test_runtime_constants_come_from_canonical_contract(self) -> None:
        self.assertEqual("ATLAS_ARGUS_EXECUTION", EXECUTION_CONTRACT["contract_id"])
        self.assertEqual(tuple(EXECUTION_CONTRACT["pre_execution_flow"]), PRE_EXECUTION_FLOW)
        self.assertEqual(EXECUTION_CONTRACT["approval"]["key"], ARGUS_APPROVAL)

    def test_remote_capability_policy_is_one_time_scoped_and_expiring(self) -> None:
        policy = EXECUTION_CONTRACT["remote_capability"]
        self.assertEqual(2, policy["version"])
        self.assertEqual("HMAC-SHA256", policy["algorithm"])
        self.assertEqual("ATLAS", policy["issuer"])
        self.assertEqual("ARGUS", policy["audience"])
        self.assertEqual("intelligence_collection:execute", policy["scope"])
        self.assertTrue(policy["one_time"])
        self.assertLessEqual(policy["max_ttl_seconds"], 300)


if __name__ == "__main__":
    unittest.main()
