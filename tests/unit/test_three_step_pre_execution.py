from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / "spec/semantic-normalization.yaml"
SPINE = ROOT / "spec/execution-spine.yaml"
TRIAGE = ROOT / "spec/request-triage.yaml"
HANDOFF = ROOT / "spec/domain-handoff.yaml"
README = ROOT / "README.md"
CHATGPT = ROOT / "integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md"
SKILL = ROOT / ".agents/skills/atlas-os/SKILL.md"


class ThreeStepPreExecutionTests(unittest.TestCase):
    def test_semantic_contract_exposes_exact_three_step_pre_execution_flow(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        flow = contract["pre_execution_flow"]
        self.assertEqual(
            ["UNDERSTAND_AND_NORMALIZE", "MINIMAL_DOMAIN_FRAMING", "ROUTE"],
            [step["id"] for step in flow["steps"]],
        )
        self.assertEqual(3, len(flow["steps"]))
        self.assertEqual("ARGUS", flow["routing_targets"]["ARGUS_COLLECTION"])
        self.assertEqual("ARGUS", flow["routing_targets"]["HYBRID"])
        self.assertEqual("ATLAS_EXECUTION", flow["routing_targets"]["ATLAS_DIRECT"])
        self.assertEqual("ATLAS_EXECUTION", flow["routing_targets"]["NONE"])

    def test_three_steps_remain_minimal_and_non_researching(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        flow = contract["pre_execution_flow"]
        self.assertTrue(flow["minimal_sufficient_context"])
        self.assertTrue(flow["no_pre_route_research_loop"])
        self.assertTrue(flow["unresolved_downstream_context_is_non_blocking"])
        self.assertEqual("meaning_ambiguity", flow["normal_semantic_blocker"])

    def test_normative_specs_use_three_step_pre_execution_language(self):
        for path in (SPINE, TRIAGE, HANDOFF):
            text = path.read_text(encoding="utf-8")
            self.assertIn("UNDERSTAND_AND_NORMALIZE", text, str(path))
            self.assertIn("MINIMAL_DOMAIN_FRAMING", text, str(path))
            self.assertIn("ROUTE", text, str(path))

    def test_human_and_host_guidance_use_same_three_step_summary(self):
        phrase = "Understand + Normalize -> Minimal Domain Framing -> Route"
        for path in (README, CHATGPT, SKILL):
            self.assertIn(phrase, path.read_text(encoding="utf-8"), str(path))


if __name__ == "__main__":
    unittest.main()
