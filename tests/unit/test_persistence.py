from __future__ import annotations

import hashlib
import unittest

from atlas_runtime.persistence import build_chat_event_markdown, chat_event_path


class ChatEventPersistenceTests(unittest.TestCase):
    @staticmethod
    def _event_id(markdown: str) -> str:
        return next(line.split(": ", 1)[1] for line in markdown.splitlines() if line.startswith("event_id: "))

    def test_event_path_is_month_partitioned_and_immutable_per_turn(self) -> None:
        path = chat_event_path(
            conversation_id="conv-123",
            turn_id="7",
            timestamp_utc="2026-10-23T00:15:00Z",
        )
        self.assertEqual(
            "General/Business Intelligence/30_OPERATIONS/CHAT_LOGS/2026-10/CHAT_conv-123_T7.md",
            path,
        )

    def test_markdown_contains_complete_visible_prompt_response_and_hashes(self) -> None:
        prompt = "Assess this opportunity.\nPreserve all constraints."
        response = "Decision-grade response.\nSecond line."
        markdown = build_chat_event_markdown(
            visible_prompt=prompt,
            visible_response=response,
            conversation_id="conv-123",
            turn_id="7",
            timestamp_utc="2026-10-23T00:15:00Z",
            metadata={
                "task_id": "ATLAS-1",
                "route": "ARGUS",
                "required_quality_tier": "Q4",
                "achieved_quality_tier": "Q4",
                "quality_gate": "PASS",
                "providers": ["argus"],
                "completion_status": "COMPLETED",
            },
        )
        self.assertIn(prompt, markdown)
        self.assertIn(response, markdown)
        self.assertIn(hashlib.sha256(prompt.encode("utf-8")).hexdigest(), markdown)
        self.assertIn(hashlib.sha256(response.encode("utf-8")).hexdigest(), markdown)
        self.assertIn("required_quality_tier: Q4", markdown)
        self.assertIn("quality_gate: PASS", markdown)

    def test_serializer_ignores_private_or_secret_bearing_metadata(self) -> None:
        markdown = build_chat_event_markdown(
            visible_prompt="Visible prompt",
            visible_response="Visible response",
            conversation_id="conv-123",
            turn_id="8",
            timestamp_utc="2026-10-23T00:16:00Z",
            metadata={
                "task_id": "ATLAS-2",
                "system_prompt": "DO NOT ARCHIVE THIS SYSTEM TEXT",
                "developer_instructions": "DO NOT ARCHIVE THIS DEVELOPER TEXT",
                "chain_of_thought": "DO NOT ARCHIVE PRIVATE REASONING",
                "api_key": "sk-secret-value",
                "signed_url": "https://example.test/?sig=secret",
                "raw_tool_payload": "SECRET RAW PAYLOAD",
            },
        )
        self.assertIn("task_id: ATLAS-2", markdown)
        self.assertNotIn("DO NOT ARCHIVE", markdown)
        self.assertNotIn("sk-secret-value", markdown)
        self.assertNotIn("sig=secret", markdown)
        self.assertNotIn("SECRET RAW PAYLOAD", markdown)

    def test_serializer_is_deterministic_for_identical_inputs(self) -> None:
        kwargs = dict(
            visible_prompt="P",
            visible_response="R",
            conversation_id="conv-123",
            turn_id="9",
            timestamp_utc="2026-10-23T00:17:00Z",
            metadata={"task_id": "ATLAS-3", "route": "DIRECT_SEARCH"},
        )
        self.assertEqual(build_chat_event_markdown(**kwargs), build_chat_event_markdown(**kwargs))

    def test_event_identity_changes_when_prompt_changes_even_if_response_and_turn_match(self) -> None:
        common = dict(
            visible_response="Same response",
            conversation_id="conv-123",
            turn_id="10",
            timestamp_utc="2026-10-23T00:18:00Z",
            metadata={"task_id": "ATLAS-4"},
        )
        first = build_chat_event_markdown(visible_prompt="Prompt A", **common)
        second = build_chat_event_markdown(visible_prompt="Prompt B", **common)
        self.assertNotEqual(self._event_id(first), self._event_id(second))


if __name__ == "__main__":
    unittest.main()
