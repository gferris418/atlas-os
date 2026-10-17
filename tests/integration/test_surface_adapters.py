from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from atlas_runtime import FileSystemLibraryAdapter, get_surface_adapter


class SurfaceAdapterIntegrationTests(unittest.TestCase):
    def test_each_supported_surface_starts_through_the_same_plan_gate(self) -> None:
        tasks = [{"id": "answer", "status": "PENDING", "dependencies": []}]
        for surface in ("chatgpt", "codex", "work"):
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
