from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "spec/chat-event-persistence.yaml"
MANIFEST = ROOT / "atlas-os.yaml"
ACCESS_ASIA = ROOT / "integrations/access-asia.yaml"


class ChatEventPersistenceConformanceTests(unittest.TestCase):
    def test_contract_is_normative_and_registered(self) -> None:
        self.assertTrue(CONTRACT.is_file())
        contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(contract["normative"])
        self.assertIn("spec/chat-event-persistence.yaml", manifest["specifications"])

    def test_completed_turns_are_atomic_immutable_events_not_per_token_writes(self) -> None:
        policy = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))["contract"]
        self.assertEqual("COMPLETED_USER_ASSISTANT_TURN", policy["event_boundary"])
        self.assertEqual("ONE_IMMUTABLE_MARKDOWN_FILE_PER_COMPLETED_TURN", policy["storage_model"])
        self.assertTrue(policy["per_token_persistence_prohibited"])
        self.assertTrue(policy["retries_must_be_idempotent"])

    def test_only_user_visible_content_is_archived(self) -> None:
        policy = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(["complete_user_visible_prompt", "complete_final_user_visible_response"], policy["required_content"])
        prohibited = set(policy["prohibited_content"])
        self.assertTrue({
            "hidden_chain_of_thought",
            "system_instructions",
            "developer_instructions",
            "credentials_or_tokens",
            "temporary_signed_urls",
            "raw_secret_bearing_tool_payloads",
        }.issubset(prohibited))

    def test_host_boundary_prevents_false_background_persistence_claims(self) -> None:
        policy = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))["contract"]
        self.assertEqual(["NOT_REQUIRED", "PENDING", "VERIFIED", "FAILED", "UNAVAILABLE"], policy["persistence_states"])
        self.assertTrue(policy["host_boundary"]["no_post_turn_write_hook_means_no_continuous_persistence_claim"])
        self.assertTrue(policy["host_boundary"]["verified_requires_durable_write_receipt"])

    def test_access_asia_maps_chat_events_to_sharepoint(self) -> None:
        profile = yaml.safe_load(ACCESS_ASIA.read_text(encoding="utf-8"))
        archive = profile["chat_event_archive"]
        self.assertEqual("SHAREPOINT", profile["persistence_routing"]["CONVERSATION_EVENT"])
        self.assertEqual(
            "General/Business Intelligence/30_OPERATIONS/CHAT_LOGS/YYYY-MM/CHAT_<conversation-id>_T<turn-number>.md",
            archive["path_template"],
        )
        self.assertEqual("ATLAS", archive["writer_authority"])
        self.assertEqual("immutable_per_completed_turn", archive["mutation_model"])


if __name__ == "__main__":
    unittest.main()
