from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "atlas-os.yaml"
SEMANTIC = ROOT / "spec/semantic-normalization.yaml"
DOMAIN_CONTEXT = ROOT / "spec/domain-context-services.yaml"
CLASSIFICATION = ROOT / "spec/classification.yaml"
DOMAIN_PRACTICES = ROOT / "spec/domain-practices.yaml"
SPINE = ROOT / "spec/execution-spine.yaml"


class SemanticNormalizationContractTests(unittest.TestCase):
    def test_manifest_registers_semantic_normalization(self):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            "spec/semantic-normalization.yaml",
            manifest["architecture"]["semantic_normalization"],
        )

    def test_normalization_preserves_context_and_prohibits_fact_creation(self):
        spec = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))
        contract = spec["contract"]
        self.assertTrue(contract["preserve_raw_input"])
        self.assertTrue(contract["semantic_drift_prohibited"])
        self.assertTrue(contract["invented_facts_prohibited"])
        self.assertTrue(contract["record_material_corrections"])
        self.assertTrue(contract["preserve_ambiguity_when_unresolved"])
        self.assertIn("original_input", contract["output_sections"])
        self.assertIn("normalized_input", contract["output_sections"])
        self.assertIn("prohibited_inferences", contract["output_sections"])

    def test_generic_context_separates_sector_industry_product_and_capability(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        facets = contract["semantic_facets"]
        for facet in (
            "domain",
            "jurisdiction",
            "buyer_or_end_user_sector",
            "supply_side_sector",
            "operator_industry",
            "supplier_industry",
            "product_or_service",
            "platform_or_system",
            "operating_environment",
            "capability",
        ):
            self.assertIn(facet, facets)
        self.assertEqual("separate", facets["buyer_or_end_user_sector"]["relationship_to_supply_side_sector"])
        self.assertTrue(contract["semantic_invariants"]["sector_is_not_industry"])
        self.assertTrue(contract["semantic_invariants"]["industry_is_not_product"])
        self.assertTrue(contract["semantic_invariants"]["product_is_not_capability"])

    def test_classification_stack_is_multi_axial_and_contextual(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        stack = contract["classification_context"]
        for key in (
            "international_activity",
            "national_activity",
            "regional_activity",
            "north_america_activity",
            "international_product_service",
            "regional_product_service",
            "procurement_global",
            "procurement_regional",
            "customs_trade",
            "defense_logistics",
        ):
            self.assertIn(key, stack)
        self.assertEqual("taxonomy.un-isic", stack["international_activity"])
        self.assertEqual("taxonomy.un-cpc", stack["international_product_service"])
        self.assertEqual("taxonomy.unspsc", stack["procurement_global"])
        self.assertEqual("taxonomy.wco-hs", stack["customs_trade"])
        self.assertEqual("taxonomy.nato-codification-system", stack["defense_logistics"])
        self.assertTrue(contract["classification_rules"]["unresolved_codes_must_not_be_guessed"])
        self.assertTrue(contract["classification_rules"]["cross_scheme_equivalence_must_not_be_assumed"])

    def test_best_practice_lenses_are_generic_and_non_binding(self):
        contract = yaml.safe_load(SEMANTIC.read_text(encoding="utf-8"))["contract"]
        lenses = contract["international_best_practice_lenses"]
        for lens in (
            "requirements_and_use_case",
            "lifecycle_and_total_cost",
            "safety_and_risk",
            "quality_and_assurance",
            "interoperability_and_open_architecture",
            "cybersecurity_and_information_assurance",
            "maintainability_and_supportability",
            "human_factors_and_accessibility",
            "sustainability_and_environment",
            "testing_acceptance_and_validation",
            "configuration_and_change_management",
        ):
            self.assertIn(lens, lenses)
        self.assertTrue(contract["best_practice_rules"]["context_lens_not_requirement"])
        self.assertTrue(contract["best_practice_rules"]["applicability_must_be_assessed"])
        self.assertTrue(contract["best_practice_rules"]["current_official_sources_preferred"])

    def test_existing_specs_delegate_to_semantic_normalization(self):
        domain_context = DOMAIN_CONTEXT.read_text(encoding="utf-8")
        classification = CLASSIFICATION.read_text(encoding="utf-8")
        domain_practices = DOMAIN_PRACTICES.read_text(encoding="utf-8")
        spine = SPINE.read_text(encoding="utf-8")
        self.assertIn("spec/semantic-normalization.yaml", domain_context)
        self.assertIn("buyer/end-user sector", domain_context)
        self.assertIn("supply-side sector", domain_context)
        self.assertIn("semantic normalization", classification.lower())
        self.assertIn("best practice is context, not a binding requirement", domain_practices.lower())
        self.assertIn("semantic_normalization", spine.lower())
        self.assertIn("whole-context", spine.lower())


if __name__ == "__main__":
    unittest.main()
