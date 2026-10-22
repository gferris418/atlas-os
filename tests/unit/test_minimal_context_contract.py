from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / "spec/semantic-normalization.yaml"
CHATGPT = ROOT / "integrations/chatgpt/ATLAS-CHATGPT-INSTRUCTIONS.md"
README = ROOT / "README.md"


class MinimalContextContractTests(unittest.TestCase):
    def test_semantic_contract_requires_minimal_material_context(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        rule = contract["context_minimization"]
        self.assertTrue(rule["minimal_sufficient_context"])
        self.assertTrue(rule["materiality_required"])
        self.assertTrue(rule["skip_low_value_enrichment"])
        self.assertTrue(rule["do_not_enumerate_irrelevant_taxonomies"])
        self.assertTrue(rule["do_not_expand_standards_without_material_need"])
        self.assertTrue(rule["do_not_add_context_just_because_available"])
        self.assertEqual("meaning_or_downstream_decision_impact", rule["inclusion_threshold"])

    def test_classifications_and_best_practices_are_proportional(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        self.assertTrue(contract["classification_rules"]["only_material_schemes"])
        self.assertTrue(contract["best_practice_rules"]["only_material_lenses"])
        self.assertTrue(contract["standards_and_framework_context"]["minimal_material_set"])

    def test_host_guidance_uses_simple_minimal_context_rule(self):
        chatgpt = CHATGPT.read_text(encoding="utf-8").lower()
        readme = README.read_text(encoding="utf-8").lower()
        self.assertIn("minimal sufficient context", chatgpt)
        self.assertIn("skip unnecessary context", chatgpt)
        self.assertIn("minimal sufficient context", readme)


if __name__ == "__main__":
    unittest.main()
