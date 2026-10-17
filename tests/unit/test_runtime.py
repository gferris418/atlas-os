from __future__ import annotations

import unittest

from atlas_runtime import (
    ApprovalRequired,
    CanonicalRevisionInUse,
    StateStore,
    align_domain_practices,
    assess_completeness,
    build_plan,
    can_transition_release,
    classify_domain_context,
    classify_task,
    create_dashboard,
    determine_execution_depth,
    normalize_intent,
    require_approval,
    route_capability,
    verify_evidence,
)


class ContextTests(unittest.TestCase):
    def test_critical_literals_survive_normalization(self) -> None:
        text = "Ship  v2.0.0-rc.1 on 2026-10-17 with `MIG-029` at 95%."
        result = normalize_intent(text)
        for literal in ("2.0", "0", "rc", "1", "2026", "10", "17", "`MIG-029`", "95%"):
            self.assertIn(literal, result["normalized"])
        self.assertEqual(text, result["original"])

    def test_completeness_only_questions_material_dimensions(self) -> None:
        result = assess_completeness({
            "what": "validate repository",
            "material_dimensions": ["what", "where", "how"],
            "safe_assumptions": {"where": "current checkout"},
        })
        self.assertEqual(["how"], result["questions"])
        self.assertEqual("current checkout", result["assumptions"][0]["value"])
        self.assertNotIn("who", result["questions"])


class PlanningTests(unittest.TestCase):
    def test_dependency_order_is_stable(self) -> None:
        graph = [
            {"id": "verify", "dependencies": ["build", "test"]},
            {"id": "test", "dependencies": ["authority"]},
            {"id": "build", "dependencies": ["authority"]},
            {"id": "authority", "dependencies": []},
        ]
        order = build_plan(graph)
        self.assertEqual("authority", order[0])
        self.assertEqual("verify", order[-1])
        self.assertLess(order.index("build"), order.index("verify"))
        self.assertLess(order.index("test"), order.index("verify"))

    def test_cycle_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_plan([
                {"id": "a", "dependencies": ["b"]},
                {"id": "b", "dependencies": ["a"]},
            ])


class RoutingTests(unittest.TestCase):
    def test_authoritative_available_capability_wins(self) -> None:
        selected = route_capability("private_research", [
            {"id": "model", "capabilities": ["private_research"], "authority": "model"},
            {"id": "connector", "capabilities": ["private_research"], "authority": "connected"},
            {"id": "denied", "capabilities": ["private_research"], "authority": "user", "permission": "denied"},
        ])
        self.assertEqual("connector", selected["id"])

    def test_unavailable_capability_fails_explicitly(self) -> None:
        with self.assertRaises(LookupError):
            route_capability("publish", [])


class EvidenceAndApprovalTests(unittest.TestCase):
    def test_assumption_does_not_become_verified_without_check(self) -> None:
        evidence = {"class": "ASSUMED", "claim": "service is healthy"}
        self.assertEqual("ASSUMED", verify_evidence(evidence)["class"])
        self.assertEqual(
            "ASSUMED",
            verify_evidence(evidence, {"passed": True, "provenance": None})["class"],
        )

    def test_verified_requires_pass_and_provenance(self) -> None:
        result = verify_evidence(
            {"class": "SUPPORTED", "claim": "tests pass"},
            {"passed": True, "provenance": {"command": "python -m unittest"}},
        )
        self.assertEqual("VERIFIED", result["class"])

    def test_high_impact_action_requires_scoped_approval(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("publish")
        self.assertTrue(require_approval("publish", {"status": "APPROVED", "scope": ["publish"]}))
        self.assertTrue(require_approval("analyze"))


class DomainPracticeTests(unittest.TestCase):
    def test_substantive_task_selects_applicable_authoritative_frameworks(self) -> None:
        result = align_domain_practices(
            "artificial-intelligence",
            [
                {
                    "id": "framework.iso-iec-42001",
                    "domains": ["artificial-intelligence"],
                    "status": "active",
                    "authority": "international-standard",
                    "official_source": "https://www.iso.org/standard/81230.html",
                    "version": "current-official",
                },
                {
                    "id": "framework.blog-advice",
                    "domains": ["artificial-intelligence"],
                    "status": "active",
                    "authority": "community",
                    "official_source": "https://example.invalid/advice",
                    "version": "unknown",
                },
            ],
            substantive=True,
        )
        self.assertEqual("ALIGNED", result["status"])
        self.assertEqual(["framework.iso-iec-42001"], result["frameworks"])
        self.assertEqual("UNVERIFIED", result["compliance"])

    def test_missing_framework_requires_authoritative_research(self) -> None:
        result = align_domain_practices("quantum-maritime-law", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", result["status"])
        self.assertIn("international", result["next_action"].lower())

    def test_l0_task_does_not_create_framework_bureaucracy(self) -> None:
        result = align_domain_practices("unit-conversion", [], substantive=False)
        self.assertEqual("NOT_REQUIRED", result["status"])

    def test_compliance_requires_verification_evidence(self) -> None:
        result = align_domain_practices(
            "information-security",
            [{
                "id": "framework.iso-iec-27001",
                "domains": ["information-security"],
                "status": "active",
                "authority": "international-standard",
                "official_source": "https://www.iso.org/standard/27001",
                "version": "current-official",
            }],
            substantive=True,
            verification={"passed": True, "evidence": ["audit-report"]},
        )
        self.assertEqual("VERIFIED", result["compliance"])


class DomainClassificationTests(unittest.TestCase):
    def test_classification_is_multi_axial_and_exposes_missing_context(self) -> None:
        records = [
            {
                "id": "classification.geo.bd",
                "status": "active",
                "facet": "jurisdiction",
                "taxonomy": "taxonomy.iso-3166-1",
                "code": "BD",
                "label": "Bangladesh",
                "triggers": ["bangladesh"],
            },
            {
                "id": "classification.industry.defence-activities",
                "status": "active",
                "facet": "operator-industry",
                "taxonomy": "taxonomy.un-isic",
                "code": "8422",
                "label": "Defence activities",
                "triggers": ["navy", "naval"],
                "risk_flags": ["defense", "national-security"],
            },
            {
                "id": "classification.capability.coastal-surveillance-radar",
                "status": "active",
                "facet": "capability",
                "taxonomy": "taxonomy.atlas-capability-skos",
                "code": "capability.coastal-surveillance-radar",
                "label": "Coastal surveillance radar",
                "match_all": ["coastal", "surveillance", "radar"],
                "risk_flags": ["defense", "dual-use", "operational-security"],
            },
            {
                "id": "classification.product.radar-hs",
                "status": "active",
                "facet": "product-or-service",
                "taxonomy": "taxonomy.wco-hs",
                "code": "8526",
                "label": "Radar apparatus and related radio apparatus",
                "triggers": ["radar"],
                "conditions": ["cross-border-trade-or-customs"],
            },
        ]
        result = classify_domain_context(
            "coastal surveillance radar for Bangladesh navy",
            records,
            required_facets=("jurisdiction", "operator-industry", "capability", "lifecycle-stage"),
        )
        self.assertEqual("PARTIAL", result["status"])
        self.assertEqual(["lifecycle-stage"], result["unresolved_facets"])
        self.assertEqual("BD", result["facets"]["jurisdiction"][0]["code"])
        self.assertEqual("8422", result["facets"]["operator-industry"][0]["code"])
        self.assertIn("operational-security", result["risk_flags"])
        self.assertEqual(
            ["classification.product.radar-hs"],
            [item["id"] for item in result["conditional_candidates"]],
        )

    def test_unknown_domain_requires_taxonomy_research(self) -> None:
        result = classify_domain_context("unmapped specialist system", [], substantive=True)
        self.assertEqual("RESEARCH_REQUIRED", result["status"])
        self.assertIn("authoritative", result["next_action"].lower())

    def test_non_substantive_task_does_not_force_classification(self) -> None:
        result = classify_domain_context("convert one metre to centimetres", [], substantive=False)
        self.assertEqual("NOT_REQUIRED", result["status"])


class PersistenceAndReleaseTests(unittest.TestCase):
    def test_task_and_canonical_namespaces_do_not_collide(self) -> None:
        store = StateStore()
        store.save_task("same", {"status": "ACTIVE"})
        with self.assertRaises(ValueError):
            store.save_canonical("same", {"status": "ACTIVE"})

    def test_active_dependency_prevents_archive(self) -> None:
        store = StateStore(canonical_state={"rev-1": {"status": "ACTIVE", "active_dependents": ["rev-2"]}})
        with self.assertRaises(CanonicalRevisionInUse):
            store.archive_canonical("rev-1")

    def test_open_blocker_prevents_release(self) -> None:
        self.assertFalse(can_transition_release("VERIFIED", "RELEASED", ["MIG-029"]))
        self.assertTrue(can_transition_release("VERIFIED", "RELEASED", []))


class ClassificationAndDashboardTests(unittest.TestCase):
    def test_task_classification_is_multi_label(self) -> None:
        labels = classify_task("Research and compare options, then write a report")
        self.assertIn("RESEARCH", labels)
        self.assertIn("ANALYSIS", labels)
        self.assertIn("MULTI_STAGE", labels)

    def test_depth_is_proportional(self) -> None:
        self.assertEqual("L0", determine_execution_depth())
        self.assertEqual("L2", determine_execution_depth(steps=4))
        self.assertEqual("L4", determine_execution_depth(risk="critical"))

    def test_substantive_task_initializes_dashboard(self) -> None:
        dashboard = create_dashboard("Build repository", progress=0)
        self.assertEqual("ATLAS", dashboard["system"])
        self.assertIsNone(create_dashboard("Convert units", substantive=False))


if __name__ == "__main__":
    unittest.main()

