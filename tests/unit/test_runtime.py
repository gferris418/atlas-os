from __future__ import annotations

import os
import unittest
from itertools import permutations
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from atlas_runtime import (
    ApprovalRequired,
    CanonicalRevisionInUse,
    FileSystemLibraryAdapter,
    StateStore,
    align_domain_practices,
    assess_completeness,
    build_plan,
    can_transition_release,
    classify_action,
    classify_domain_context,
    classify_task,
    confirm_library_save,
    create_dashboard,
    determine_execution_depth,
    normalize_intent,
    prepare_library_record,
    render_dashboard,
    require_approval,
    route_capability,
    route_taxonomy_layer,
    select_next_work_unit,
    select_output_profile,
    validate_output_record,
    verify_evidence,
)


def governed_taxonomies() -> list[dict[str, str]]:
    return [
        {
            "id": taxonomy_id,
            "status": "active",
            "authority": "canonical" if taxonomy_id == "taxonomy.atlas-capability-skos" else "official-primary",
            "version_policy": "current-official",
            "official_source": "https://example.invalid/taxonomy",
            "classification_scope": scope,
        }
        for taxonomy_id, scope in (
            ("taxonomy.iso-3166-1", "geography"),
            ("taxonomy.un-isic", "economic-activity"),
            ("taxonomy.wco-hs", "customs"),
            ("taxonomy.atlas-capability-skos", "internal-capability"),
        )
    ]


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

    def test_duplicate_work_unit_identifiers_are_rejected_before_planning(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique"):
            build_plan([
                {"id": "same", "dependencies": []},
                {"id": "same", "dependencies": []},
            ])

    def test_atomic_plan_allows_only_one_active_work_unit(self) -> None:
        with self.assertRaises(ValueError):
            select_next_work_unit([
                {"id": "a", "status": "ACTIVE", "dependencies": []},
                {"id": "b", "status": "ACTIVE", "dependencies": []},
            ], plan_id="plan-1", plan_status="READY")

    def test_atomic_plan_rejects_unknown_or_stalled_task_states(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid work unit status"):
            select_next_work_unit(
                [{"id": "one", "status": "TYPO", "dependencies": []}],
                plan_id="plan-1", plan_status="READY",
            )
        with self.assertRaisesRegex(ValueError, "no executable work unit"):
            select_next_work_unit(
                [{"id": "one", "status": "BLOCKED", "dependencies": []}],
                plan_id="plan-1", plan_status="READY",
            )

    def test_atomic_plan_selects_one_ready_unit_in_plan_order(self) -> None:
        selected = select_next_work_unit([
            {"id": "understand", "status": "COMPLETED", "dependencies": []},
            {"id": "implement", "status": "PENDING", "dependencies": ["understand"]},
            {"id": "verify", "status": "PENDING", "dependencies": ["implement"]},
        ], plan_id="plan-1", plan_status="READY")
        self.assertEqual("implement", selected)

    def test_atomic_plan_rejects_active_unit_with_incomplete_dependency(self) -> None:
        with self.assertRaises(ValueError):
            select_next_work_unit([
                {"id": "understand", "status": "PENDING", "dependencies": []},
                {"id": "implement", "status": "ACTIVE", "dependencies": ["understand"]},
            ], plan_id="plan-1", plan_status="READY")

    def test_completed_atomic_plan_has_no_next_unit(self) -> None:
        self.assertIsNone(select_next_work_unit([
            {"id": "done", "status": "COMPLETED", "dependencies": []},
        ], plan_id="plan-1", plan_status="READY"))

    def test_atomic_plan_requires_concrete_plan_identity(self) -> None:
        tasks = [{"id": "one", "status": "PENDING", "dependencies": []}]
        with self.assertRaises((TypeError, ValueError)):
            select_next_work_unit(tasks, plan_id="", plan_status="READY")


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

    def test_routing_is_independent_of_candidate_order(self) -> None:
        capabilities = [
            {
                "id": "connected-slow",
                "capabilities": ["research"],
                "authority": "connected",
                "risk": 1,
                "latency": 20,
            },
            {
                "id": "connected-fast",
                "capabilities": ["research"],
                "authority": "connected",
                "risk": 1,
                "latency": 5,
            },
            {
                "id": "connected-risky",
                "capabilities": ["research"],
                "authority": "connected",
                "risk": 2,
                "latency": 1,
            },
        ]

        selected_ids = {
            route_capability("research", ordering)["id"]
            for ordering in permutations(capabilities)
        }

        self.assertEqual({"connected-fast"}, selected_ids)

    def test_routing_has_a_total_identifier_fallback(self) -> None:
        tied = [
            {
                "id": identifier,
                "capabilities": ["research"],
                "authority": "official",
                "risk": 1,
                "latency": 5,
            }
            for identifier in ("alpha", "zeta")
        ]

        selected_ids = {
            route_capability("research", ordering)["id"]
            for ordering in permutations(tied)
        }

        self.assertEqual({"zeta"}, selected_ids)


class EvidenceAndApprovalTests(unittest.TestCase):
    def test_arbitrary_operation_is_governed_by_semantic_action_class(self) -> None:
        classification = classify_action(
            "MERGE_CANONICAL_ENTITY",
            action_classes=["major_canonical_state_change"],
        )
        self.assertEqual(["major_canonical_state_change"], classification["action_classes"])
        self.assertTrue(classification["approval_required"])
        with self.assertRaises(ApprovalRequired):
            require_approval(
                "MERGE_CANONICAL_ENTITY",
                action_classes=["major_canonical_state_change"],
            )

    def test_action_classification_is_required_and_fail_closed(self) -> None:
        with self.assertRaises(ApprovalRequired):
            require_approval("UNREGISTERED_OPERATION")
        with self.assertRaises(ValueError):
            classify_action("UNREGISTERED_OPERATION", action_classes=["unknown_class"])
        self.assertTrue(
            require_approval("ANALYZE", action_classes=["reversible_analysis"])
        )

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
            require_approval("publish", action_classes=["publication"])
        approval = {
            "id": "APR-PUBLISH-001",
            "required": True,
            "reason": "Publish the reviewed release",
            "scope": ["publish"],
            "status": "APPROVED",
            "requested_at": "2026-10-18T05:00:00Z",
            "approved_at": "2026-10-18T05:01:00Z",
            "action_type": "publish",
            "target_id": "release:atlas-os:2.0.0-rc.9",
            "input_sha256": "sha256:" + "a" * 64,
            "precondition_revision": "fffb1836",
            "approver_identity": "user:maintainer",
            "issued_at": "2026-10-18T05:01:00Z",
            "expires_at": "2099-10-18T06:01:00Z",
            "policy_revision": "approvals-v2",
            "source_task_id": "TASK-ATLAS-PUBLISH", "source_plan_id": "plan-publish",
            "source_work_unit_id": "unit-publish", "handoff_id": None,
        }
        self.assertTrue(require_approval(
            "publish",
            approval,
            action_classes=["publication"],
            target_id="release:atlas-os:2.0.0-rc.9",
            input_sha256="sha256:" + "a" * 64,
            precondition_revision="fffb1836",
            policy_revision="approvals-v2",
            source_task_id="TASK-ATLAS-PUBLISH", source_plan_id="plan-publish",
            source_work_unit_id="unit-publish", handoff_id=None,
        ))
        self.assertTrue(
            require_approval("analyze", action_classes=["reversible_analysis"])
        )

    def test_high_impact_approval_is_bound_and_unexpired(self) -> None:
        approval = {
            "status": "APPROVED",
            "scope": ["delete"],
            "action_type": "delete",
            "target_id": "record:ARGUS-001",
            "input_sha256": "sha256:" + "b" * 64,
            "precondition_revision": "rev-7",
            "approver_identity": "user:maintainer",
            "issued_at": "2026-10-18T05:00:00Z",
            "expires_at": "2000-10-18T05:15:00Z",
            "policy_revision": "approvals-v2",
            "source_task_id": "TASK-ARGUS-DELETE", "source_plan_id": "plan-delete",
            "source_work_unit_id": "unit-delete", "handoff_id": "HANDOFF-ARGUS-READY",
        }
        common = {
            "target_id": "record:ARGUS-001",
            "input_sha256": "sha256:" + "b" * 64,
            "precondition_revision": "rev-7",
            "policy_revision": "approvals-v2",
            "source_task_id": "TASK-ARGUS-DELETE", "source_plan_id": "plan-delete",
            "source_work_unit_id": "unit-delete", "handoff_id": "HANDOFF-ARGUS-READY",
        }
        for field, value in (
            ("target_id", "record:OTHER"),
            ("input_sha256", "sha256:" + "c" * 64),
            ("precondition_revision", "rev-8"),
            ("policy_revision", "approvals-v3"),
        ):
            request = dict(common)
            request[field] = value
            with self.subTest(field=field), self.assertRaises(ApprovalRequired):
                require_approval(
                    "delete",
                    approval,
                    action_classes=["destructive_action"],
                    **request,
                )

    def test_caller_cannot_replay_expired_approval_with_historical_time(self) -> None:
        approval = {
            "id": "APR-EXPIRED-001", "required": True, "reason": "old approval",
            "scope": ["delete"], "status": "APPROVED",
            "requested_at": "2000-01-01T00:00:00Z", "approved_at": "2000-01-01T00:01:00Z",
            "action_type": "delete", "target_id": "record:ARGUS-001",
            "input_sha256": "sha256:" + "b" * 64, "precondition_revision": "rev-7",
            "approver_identity": "user:maintainer", "issued_at": "2000-01-01T00:01:00Z",
            "expires_at": "2000-01-02T00:01:00Z", "policy_revision": "approvals-v2",
            "source_task_id": "TASK-ARGUS-DELETE", "source_plan_id": "plan-delete",
            "source_work_unit_id": "unit-delete", "handoff_id": "HANDOFF-ARGUS-READY",
        }
        with self.assertRaises(ApprovalRequired):
            require_approval(
                "delete", approval, target_id="record:ARGUS-001",
                action_classes=["destructive_action"],
                input_sha256="sha256:" + "b" * 64,
                precondition_revision="rev-7", policy_revision="approvals-v2",
                source_task_id="TASK-ARGUS-DELETE", source_plan_id="plan-delete",
                source_work_unit_id="unit-delete", handoff_id="HANDOFF-ARGUS-READY",
            )


class OutputProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = [
            {
                "id": "output.answer-concise",
                "status": "active",
                "applies_to": ["ANSWER"],
                "format": "markdown",
                "priority": 10,
                "required_fields": ["result", "verification"],
                "machine_readable": False,
            },
            {
                "id": "output.decision-brief",
                "status": "active",
                "applies_to": ["DECISION"],
                "format": "markdown",
                "priority": 100,
                "required_fields": ["result", "evidence", "risks", "next_actions", "verification"],
                "machine_readable": False,
            },
            {
                "id": "output.data-structured",
                "status": "active",
                "applies_to": ["DATA"],
                "format": "json",
                "priority": 90,
                "required_fields": ["result", "verification"],
                "machine_readable": True,
            },
        ]

    def test_profile_selection_uses_task_fit_without_overriding_user_choice(self) -> None:
        selected = select_output_profile(["ANALYSIS", "DECISION"], self.profiles)
        self.assertEqual("output.decision-brief", selected["id"])
        requested = select_output_profile(
            ["DECISION"], self.profiles, requested_id="output.answer-concise"
        )
        self.assertEqual("output.answer-concise", requested["id"])

    def test_machine_readable_request_selects_structured_profile(self) -> None:
        selected = select_output_profile(["DATA"], self.profiles, machine_readable=True)
        self.assertEqual("output.data-structured", selected["id"])

    def test_output_validation_checks_only_profile_requirements(self) -> None:
        profile = self.profiles[1]
        incomplete = validate_output_record(
            {
                "profile": profile["id"],
                "status": "COMPLETED",
                "result": {"recommendation": "Proceed"},
                "risks": ["Cost"],
                "next_actions": ["Approve"],
                "verification": {"status": "PASS"},
            },
            profile,
        )
        self.assertFalse(incomplete["valid"])
        self.assertIn("evidence", incomplete["errors"][0])

        complete = validate_output_record(
            {
                "profile": profile["id"],
                "status": "COMPLETED",
                "result": {"recommendation": "Proceed"},
                "evidence": ["assessment"],
                "risks": ["Cost"],
                "next_actions": ["Approve"],
                "verification": {"status": "PASS"},
            },
            profile,
        )
        self.assertTrue(complete["valid"])


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
    def test_taxonomy_router_emits_governed_four_level_hierarchy(self) -> None:
        route = route_taxonomy_layer(
            "coastal surveillance radar for Bangladesh navy",
            [{
                "id": "taxonomy-route.radar",
                "status": "active",
                "domain": "government-public-sector",
                "sub_domain": "defense-national-security",
                "vertical": "maritime-defense",
                "artifact_class": "surveillance-sensor-capability",
                "match_all": ["coastal", "surveillance", "radar"],
                "candidate_taxonomies": ["taxonomy.iso-3166-1", "taxonomy.un-isic"],
                "required_facets": ["jurisdiction", "operator-industry"],
                "material_dimensions": ["what", "why"],
            }],
            governed_taxonomies(),
        )
        self.assertEqual("ROUTED", route["status"])
        self.assertEqual(
            {
                "domain": "government-public-sector",
                "sub_domain": "defense-national-security",
                "vertical": "maritime-defense",
                "artifact_class": "surveillance-sensor-capability",
            },
            route["hierarchy"],
        )

    def test_classification_rejects_ungoverned_taxonomy_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "ungoverned taxonomy"):
            classify_domain_context(
                "radar",
                [{
                    "id": "classification.invalid",
                    "status": "active",
                    "facet": "capability",
                    "taxonomy": "taxonomy.unregistered",
                    "code": "invalid",
                    "label": "Invalid",
                    "triggers": ["radar"],
                }],
                taxonomies=governed_taxonomies(),
                required_facets=("capability",),
            )

    def test_taxonomy_selection_precedes_ordered_domain_facets(self) -> None:
        records = [
            {
                "id": "classification.capability.coastal-surveillance-radar",
                "status": "active",
                "facet": "capability",
                "taxonomy": "taxonomy.atlas-capability-skos",
                "code": "capability.coastal-surveillance-radar",
                "label": "Coastal surveillance radar",
                "match_all": ["coastal", "surveillance", "radar"],
            },
            {
                "id": "classification.industry.defence-activities",
                "status": "active",
                "facet": "operator-industry",
                "taxonomy": "taxonomy.un-isic",
                "code": "8422",
                "label": "Defence activities",
                "triggers": ["navy"],
            },
            {
                "id": "classification.geo.bd",
                "status": "active",
                "facet": "jurisdiction",
                "taxonomy": "taxonomy.iso-3166-1",
                "code": "BD",
                "label": "Bangladesh",
                "triggers": ["bangladesh"],
            },
        ]

        result = classify_domain_context(
            "coastal surveillance radar for Bangladesh navy",
            records,
            taxonomies=governed_taxonomies(),
            required_facets=("jurisdiction", "operator-industry", "capability"),
        )

        self.assertEqual(
            [
                "TAXONOMY_SELECTION",
                "JURISDICTION_CLASSIFICATION",
                "OPERATOR_INDUSTRY_CLASSIFICATION",
                "SUPPLIER_INDUSTRY_CLASSIFICATION",
                "PRODUCT_OR_SERVICE_CLASSIFICATION",
                "CAPABILITY_CLASSIFICATION",
                "LIFECYCLE_STAGE_CLASSIFICATION",
                "STAKEHOLDER_CLASSIFICATION",
                "INFORMATION_SENSITIVITY_CLASSIFICATION",
            ],
            result.get("classification_sequence"),
        )
        self.assertEqual(
            ["jurisdiction", "operator-industry", "capability"],
            list(result["facets"]),
        )

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
            taxonomies=governed_taxonomies(),
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
        result = classify_domain_context(
            "unmapped specialist system", [], taxonomies=governed_taxonomies(), substantive=True
        )
        self.assertEqual("RESEARCH_REQUIRED", result["status"])
        self.assertIn("authoritative", result["next_action"].lower())

    def test_non_substantive_task_does_not_force_classification(self) -> None:
        result = classify_domain_context(
            "convert one metre to centimetres", [], taxonomies=[], substantive=False
        )
        self.assertEqual("NOT_REQUIRED", result["status"])

    def test_classification_without_material_facet_policy_is_not_complete(self) -> None:
        result = classify_domain_context(
            "Bangladesh",
            [{
                "id": "classification.geo.bd",
                "status": "active",
                "facet": "jurisdiction",
                "taxonomy": "taxonomy.iso-3166-1",
                "code": "BD",
                "label": "Bangladesh",
                "triggers": ["bangladesh"],
            }],
            taxonomies=governed_taxonomies(),
        )
        self.assertEqual("PARTIAL", result["status"])
        self.assertIn("material", result["next_action"].lower())


class PersistenceAndReleaseTests(unittest.TestCase):
    def test_output_is_routed_to_profile_library_collection_and_format(self) -> None:
        record = prepare_library_record(
            "radar-requirements",
            {
                "id": "output.technical-spec",
                "format": "markdown",
                "supported_formats": ["markdown", "json", "yaml"],
                "library_collection": "specifications",
                "file_extension": "md",
            },
            library_root="library",
        )
        self.assertEqual("READY", record["delivery_status"])
        self.assertEqual("markdown", record["format"])
        self.assertEqual("library/specifications/radar-requirements.md", record["location"])
        with self.assertRaises(ValueError):
            confirm_library_save(record, {"claim": True})

        with TemporaryDirectory() as temporary_directory:
            adapter = FileSystemLibraryAdapter(Path(temporary_directory))
            saved = adapter.save(record, "verified content")
            target = Path(temporary_directory) / record["location"]
            self.assertEqual("verified content", target.read_text(encoding="utf-8"))
            self.assertEqual("SAVED", saved["delivery_status"])
            self.assertEqual(record["location"], saved["persistence_evidence"]["location"])
            self.assertRegex(saved["persistence_evidence"]["checksum"], r"^sha256:[0-9a-f]{64}$")
            repeated = adapter.save(record, "verified content")
            self.assertEqual(saved["persistence_evidence"]["checksum"], repeated["persistence_evidence"]["checksum"])
            with self.assertRaises(FileExistsError):
                adapter.save(record, "different content")
            self.assertEqual("verified content", target.read_text(encoding="utf-8"))

    def test_library_paths_cannot_escape_declared_root(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "../outside",
            "file_extension": "md",
        }
        with self.assertRaises(ValueError):
            prepare_library_record("answer", profile)

    def test_filesystem_adapter_rejects_symlink_escape(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            outside = workspace / "outside"
            outside.mkdir()
            (workspace / "library").mkdir()
            (workspace / "library/answers").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                FileSystemLibraryAdapter(workspace).save(record, "content")
            self.assertFalse((outside / "answer.md").exists())

    def test_filesystem_adapter_rejects_symlinked_library_root(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            workspace = base / "workspace"
            outside = base / "outside"
            workspace.mkdir()
            outside.mkdir()
            (workspace / "library").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "library root"):
                FileSystemLibraryAdapter(workspace).save(record, "content")
            self.assertFalse((outside / "answers/answer.md").exists())

    def test_filesystem_adapter_rechecks_root_after_construction(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            workspace = base / "workspace"
            outside = base / "outside"
            workspace.mkdir()
            outside.mkdir()
            (workspace / "library").mkdir()
            adapter = FileSystemLibraryAdapter(workspace)
            (workspace / "library").rename(workspace / "original-library")
            (workspace / "library").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "library root"):
                adapter.save(record, "content")
            self.assertFalse((outside / "answers/answer.md").exists())

    def test_filesystem_adapter_detects_directory_swap_during_save(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            workspace = base / "workspace"
            outside = base / "outside"
            (workspace / "library/answers").mkdir(parents=True)
            outside.mkdir()
            adapter = FileSystemLibraryAdapter(workspace)
            real_link = os.link

            def swap_parent_then_link(*args: object, **kwargs: object) -> None:
                answers = workspace / "library/answers"
                answers.rename(workspace / "library/original-answers")
                answers.symlink_to(outside, target_is_directory=True)
                real_link(*args, **kwargs)

            with (
                patch("atlas_runtime.persistence.os.link", side_effect=swap_parent_then_link),
                self.assertRaisesRegex(OSError, "changed during persistence"),
            ):
                adapter.save(record, "content")
            self.assertFalse((outside / "answer.md").exists())
            self.assertFalse((workspace / "library/original-answers/answer.md").exists())

    def test_filesystem_adapter_rejects_root_move_and_symlink_back_during_save(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            workspace = base / "workspace"
            outside = base / "outside"
            (workspace / "library/answers").mkdir(parents=True)
            outside.mkdir()
            adapter = FileSystemLibraryAdapter(workspace)
            real_link = os.link

            def move_root_then_link(*args: object, **kwargs: object) -> None:
                moved = outside / "escaped-library"
                (workspace / "library").rename(moved)
                (workspace / "library").symlink_to(moved, target_is_directory=True)
                real_link(*args, **kwargs)

            with (
                patch("atlas_runtime.persistence.os.link", side_effect=move_root_then_link),
                self.assertRaisesRegex(OSError, "changed during persistence"),
            ):
                adapter.save(record, "content")
            self.assertFalse((outside / "escaped-library/answers/answer.md").exists())

    def test_filesystem_adapter_idempotent_retry_does_not_require_new_file(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        record = prepare_library_record("answer", profile)
        with TemporaryDirectory() as temporary_directory:
            adapter = FileSystemLibraryAdapter(Path(temporary_directory))
            first = adapter.save(record, "content")
            real_open = os.open

            def reject_new_files(path: object, flags: int, *args: object, **kwargs: object) -> int:
                if flags & os.O_CREAT:
                    raise PermissionError("new files are not allowed")
                return real_open(path, flags, *args, **kwargs)

            with patch("atlas_runtime.persistence.os.open", side_effect=reject_new_files):
                repeated = adapter.save(record, "content")
            self.assertEqual(
                first["persistence_evidence"]["checksum"],
                repeated["persistence_evidence"]["checksum"],
            )

    def test_supplied_timestamps_require_offsets_and_match_declared_timezone(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extension": "md",
        }
        with self.assertRaisesRegex(ValueError, "offset"):
            prepare_library_record(
                "answer", profile, timestamp="2026-10-17T23:30:00", timezone_name="UTC"
            )
        with self.assertRaisesRegex(ValueError, "RFC 3339"):
            prepare_library_record(
                "answer", profile, timestamp="2026-10-17 23:30:00+00:00", timezone_name="UTC"
            )
        with self.assertRaisesRegex(ValueError, "timezone"):
            prepare_library_record(
                "answer", profile,
                timestamp="2026-10-17T23:30:00+06:00", timezone_name="UTC",
            )
        with self.assertRaisesRegex(ValueError, "timezone"):
            create_dashboard(
                "Answer", plan_id="plan-answer", plan_status="READY",
                timestamp="2026-10-17T23:30:00+06:00", timezone_name="UTC",
            )

    def test_library_record_exposes_unavailable_or_unauthorized_storage(self) -> None:
        profile = {
            "id": "output.answer-concise",
            "format": "markdown",
            "supported_formats": ["markdown"],
            "library_collection": "answers",
            "file_extension": "md",
        }
        unavailable = prepare_library_record("answer", profile, capability_available=False)
        blocked = prepare_library_record("answer", profile, authorized=False)
        self.assertEqual("CAPABILITY_UNAVAILABLE", unavailable["delivery_status"])
        self.assertIsNone(unavailable["location"])
        self.assertEqual("BLOCKED", blocked["delivery_status"])
        self.assertIsNone(blocked["location"])

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

    def test_every_prompt_initializes_a_compact_dashboard(self) -> None:
        dashboard = create_dashboard(
            "Convert units", progress=40, active_unit="calculate", completed_units=1, total_units=2,
            substantive=False, timestamp="2026-10-17T23:30:00+06:00", duration_ms=12,
            timezone_name="Asia/Dhaka",
            input_summary="Convert 10 km to miles", processing_summary="Applying SI conversion",
            output_summary="Pending verified result", playbook="Direct calculation",
            frameworks=["SI", "ISO 80000"], sop="Plan → calculate → verify → save",
            output_profile="output.answer-concise",
            plan_id="plan-convert", plan_status="READY",
        )
        self.assertEqual("ATLAS", dashboard["system"])
        self.assertEqual("TAXONOMY_ROUTING", dashboard["active_stage"])
        self.assertEqual("[####------] 40%", dashboard["progress_visual"])
        rendered = render_dashboard(dashboard)
        self.assertIn("1/2", rendered)
        self.assertIn("calculate", rendered)
        for value in (
            "2026-10-17T23:30:00+06:00", "12 ms", "Convert 10 km to miles",
            "Applying SI conversion", "Pending verified result", "Direct calculation",
            "SI, ISO 80000", "Plan → calculate → verify → save", "output.answer-concise",
        ):
            self.assertIn(value, rendered)
        self.assertLessEqual(len(rendered.splitlines()), 8)

    def test_execution_cannot_start_before_plan_or_material_clarification(self) -> None:
        tasks = [{"id": "one", "status": "PENDING", "dependencies": []}]
        with self.assertRaises(ValueError):
            select_next_work_unit(tasks, plan_id="plan-1", plan_status="DRAFT")
        with self.assertRaises(ValueError):
            select_next_work_unit(
                tasks, plan_id="plan-1", plan_status="READY", clarification_status="PENDING"
            )


if __name__ == "__main__":
    unittest.main()

