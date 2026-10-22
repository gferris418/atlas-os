from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class AccessAsiaOperatingPolicyTests(unittest.TestCase):
    def test_operating_policy_separates_fixed_invariants_from_runtime_variables(self) -> None:
        path = ROOT / "integrations" / "access-asia" / "operating-policy.yaml"
        self.assertTrue(path.exists())
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.assertEqual("access-asia-operating-policy", data["integration_id"])
        self.assertEqual("references_only", data["fixed_invariants"]["representation"])
        self.assertEqual(
            "integrations/access-asia/system-of-record.yaml",
            data["fixed_invariants"]["authorities"]["system_of_record"],
        )
        self.assertEqual(
            "integrations/access-asia/opportunity-lifecycle.yaml",
            data["fixed_invariants"]["authorities"]["opportunity_lifecycle"],
        )
        self.assertEqual("spec/approvals.yaml", data["fixed_invariants"]["authorities"]["approvals"])
        self.assertEqual(
            "spec/execution-spine.yaml",
            data["fixed_invariants"]["authorities"]["execution_spine"],
        )

    def test_fast_path_reuses_verified_context_and_resolves_connectors_lazily(self) -> None:
        data = yaml.safe_load(
            (ROOT / "integrations" / "access-asia" / "operating-policy.yaml").read_text(encoding="utf-8")
        )
        startup = data["runtime_variables"]["startup"]
        self.assertTrue(startup["reuse_verified_context_within_session"])
        self.assertTrue(startup["resolve_connector_capabilities_lazily"])
        self.assertEqual("authority_revision_change", startup["invalidate_cached_context_on"])

    def test_retry_and_parallelism_are_bounded_and_mutations_remain_gated(self) -> None:
        data = yaml.safe_load(
            (ROOT / "integrations" / "access-asia" / "operating-policy.yaml").read_text(encoding="utf-8")
        )
        execution = data["runtime_variables"]["execution"]
        self.assertEqual(2, execution["transient_retry_limit"])
        self.assertGreaterEqual(execution["safe_read_parallelism"], 2)
        self.assertTrue(execution["parallelize_independent_safe_reads"])
        self.assertFalse(execution["parallelize_canonical_mutations"])
        self.assertTrue(execution["stop_on_ambiguous_business_exception"])

    def test_completion_requires_verified_external_state(self) -> None:
        data = yaml.safe_load(
            (ROOT / "integrations" / "access-asia" / "operating-policy.yaml").read_text(encoding="utf-8")
        )
        verification = data["runtime_variables"]["verification"]
        self.assertTrue(verification["verify_external_state_after_mutation"])
        self.assertTrue(verification["record_partial_completion_explicitly"])
        self.assertTrue(verification["resume_from_last_verified_state"])

    def test_mcp_roadmap_prioritizes_existing_systems_before_new_infrastructure(self) -> None:
        path = ROOT / "integrations" / "access-asia" / "mcp-roadmap.yaml"
        self.assertTrue(path.exists())
        data = yaml.safe_load(path.read_text(encoding="utf-8"))

        phases = data["phases"]
        self.assertEqual("stabilize_existing_connectors", phases[0]["id"])
        self.assertEqual("read_automation_and_reconciliation", phases[1]["id"])
        self.assertEqual("governed_write_automation", phases[2]["id"])
        self.assertEqual("conditional_infrastructure_expansion", phases[3]["id"])
        self.assertIn("hubspot", phases[0]["systems"])
        self.assertIn("sharepoint", phases[0]["systems"])
        self.assertIn("github", phases[0]["systems"])
        self.assertFalse(data["new_database_required_now"])

    def test_machine_contracts_register_new_access_asia_yaml(self) -> None:
        data = yaml.safe_load((ROOT / "atlas-ai.yaml").read_text(encoding="utf-8"))
        contracts = set(data["machine_contracts"])
        self.assertIn("integrations/access-asia/operating-policy.yaml", contracts)
        self.assertIn("integrations/access-asia/mcp-roadmap.yaml", contracts)


if __name__ == "__main__":
    unittest.main()
