from __future__ import annotations

import unittest
from inspect import signature
from pathlib import Path
from tempfile import TemporaryDirectory

from atlas_runtime import FileSystemLibraryAdapter, get_surface_adapter


class SurfaceAdapterIntegrationTests(unittest.TestCase):
    def test_adapter_accepts_bound_routing_approval_fields(self) -> None:
        parameters = signature(get_surface_adapter("chatgpt").start_prompt).parameters
        self.assertIn("task_id", parameters)
        self.assertIn("routing_approval_status", parameters)
        self.assertIn("routing_preview_digest", parameters)

    def test_each_supported_surface_starts_through_the_same_plan_gate(self) -> None:
        tasks = [{"id": "answer", "status": "PENDING", "dependencies": []}]
        for surface in ("chatgpt", "codex", "work", "hermes-agent", "custom-ai-tool"):
            with self.subTest(surface=surface):
                adapter = get_surface_adapter(surface)
                dashboard = adapter.start_prompt(
                    "Answer safely",
                    tasks,
                    plan_id=f"plan-{surface}",
                    timestamp="2026-10-17T23:30:00+06:00",
                    timezone_name="Asia/Dhaka",
                )
                self.assertEqual(surface, dashboard["surface"])
                self.assertEqual(f"plan-{surface}", dashboard["plan_id"])
                self.assertEqual("answer", dashboard["active_unit"])
                self.assertEqual("READY", dashboard["plan_status"])
                self.assertIn("Taxonomy UNRESOLVED", dashboard["processing_summary"])

    def test_adapter_rejects_invalid_ai_host_identifier(self) -> None:
        with self.assertRaisesRegex(ValueError, "surface identifier"):
            get_surface_adapter("Microsoft Windows")

    def test_routed_substantive_prompt_blocks_before_data_plane(self) -> None:
        tasks = [{"id": "assess", "status": "PENDING", "dependencies": []}]
        dashboard = get_surface_adapter("hermes-agent").start_prompt(
            "Assess coastal surveillance radar for Bangladesh Navy",
            tasks,
            plan_id="plan-radar",
        )

        self.assertEqual("BLOCKED", dashboard["plan_status"])
        self.assertEqual("PENDING", dashboard["clarification_status"])
        self.assertEqual("MATERIAL_CONTEXT_MATRIX", dashboard["active_stage"])
        self.assertEqual("BLOCKED", dashboard["quality_gate"])
        self.assertIn("why", dashboard["blocker_or_approval"])

    def test_ai_host_adapter_exposes_provider_routing_preview(self) -> None:
        dashboard = get_surface_adapter("hermes-agent").start_prompt(
            (
                "Find and assess public procurement opportunities for coastal "
                "surveillance radar for Bangladesh Navy using public sources only"
            ),
            [{"id": "research", "status": "PENDING", "dependencies": []}],
            plan_id="plan-bd-radar-opportunities",
            clarification_status="RESOLVED",
            timestamp="2026-10-21T22:45:00+06:00",
            timezone_name="Asia/Dhaka",
        )

        self.assertEqual("ROUTING_PREVIEW", dashboard["active_stage"])
        self.assertIn("routing_preview", dashboard)
        self.assertEqual("PROPOSED", dashboard["routing_preview"]["status"])
        self.assertEqual([], dashboard["routing_decisions"])
        self.assertIn(
            "domain-method.argus-intelligence",
            {provider["id"] for provider in dashboard["routing_preview"]["providers"]},
        )

    def test_surface_delivery_uses_real_storage_and_verified_receipt(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extensions": {"markdown": "md"},
        }
        with TemporaryDirectory() as temporary_directory:
            storage = FileSystemLibraryAdapter(Path(temporary_directory))
            result = get_surface_adapter("codex").deliver(
                "answer-001", profile, "Durable answer", storage=storage,
                timestamp="2026-10-17T23:30:00+06:00",
                timezone_name="Asia/Dhaka",
            )
            self.assertEqual("SAVED", result["delivery_status"])
            saved_path = Path(temporary_directory) / "library/answers/answer-001.md"
            self.assertEqual("Durable answer", saved_path.read_text(encoding="utf-8"))

    def test_surface_without_storage_reports_capability_unavailable(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extensions": {"markdown": "md"},
        }
        result = get_surface_adapter("chatgpt").deliver("answer-001", profile, "Answer")
        self.assertEqual("CAPABILITY_UNAVAILABLE", result["delivery_status"])

    def test_surface_blocks_execution_while_material_clarification_is_pending(self) -> None:
        tasks = [{"id": "answer", "status": "PENDING", "dependencies": []}]
        with self.assertRaises(ValueError):
            get_surface_adapter("work").start_prompt(
                "Answer safely", tasks, plan_id="plan-work", clarification_status="PENDING"
            )

    def test_surface_does_not_write_without_authorization(self) -> None:
        profile = {
            "id": "output.answer-concise", "format": "markdown",
            "supported_formats": ["markdown"], "library_collection": "answers",
            "file_extensions": {"markdown": "md"},
        }
        with TemporaryDirectory() as temporary_directory:
            storage = FileSystemLibraryAdapter(Path(temporary_directory))
            result = get_surface_adapter("codex").deliver(
                "answer-001", profile, "Answer", storage=storage, authorized=False,
            )
            self.assertEqual("BLOCKED", result["delivery_status"])
            self.assertFalse((Path(temporary_directory) / "library/answers/answer-001.md").exists())


if __name__ == "__main__":
    unittest.main()
