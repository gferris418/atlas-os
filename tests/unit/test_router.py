from __future__ import annotations

import unittest

from atlas_runtime import ARGUS_APPROVAL, EXTERNAL_ACTION_APPROVAL, choose_route


class RouterTests(unittest.TestCase):
    def test_writing_stays_native(self) -> None:
        route = choose_route("Rewrite this supplier letter formally.")
        self.assertEqual("NO_TOOL", route.mechanism)
        self.assertEqual("direct_answer", route.capability)
        self.assertFalse(route.approval_required)

    def test_current_tender_lookup_uses_direct_search(self) -> None:
        route = choose_route("Find the current Bangladesh Railway tenders.")
        self.assertEqual("DIRECT_SEARCH", route.mechanism)
        self.assertEqual("direct_search", route.capability)

    def test_structured_target_collection_requires_argus_approval(self) -> None:
        route = choose_route("Build a dossier on ST Engineering for Bangladesh opportunities.")
        self.assertEqual("ARGUS", route.mechanism)
        self.assertEqual("intelligence_collection", route.capability)
        self.assertTrue(route.approval_required)
        self.assertEqual("PENDING", route.approval_status)

        approved = choose_route(
            "Build a dossier on ST Engineering for Bangladesh opportunities.",
            approvals=(ARGUS_APPROVAL,),
        )
        self.assertEqual("APPROVED", approved.approval_status)

    def test_comparison_with_structured_collection_is_multi_capability(self) -> None:
        route = choose_route("Compare ST Engineering and L3Harris for Bangladesh opportunities.")
        self.assertEqual("MULTI_CAPABILITY", route.mechanism)
        self.assertTrue(route.approval_required)

    def test_connected_private_source_routes_to_connector(self) -> None:
        route = choose_route("Summarize our SharePoint project files.")
        self.assertEqual("CONNECTED_SOURCE", route.mechanism)

    def test_external_action_is_separately_approval_gated(self) -> None:
        route = choose_route("Send this proposal to the client.")
        self.assertEqual("EXTERNAL_ACTION", route.mechanism)
        self.assertEqual("PENDING", route.approval_status)
        approved = choose_route("Send this proposal to the client.", approvals=(EXTERNAL_ACTION_APPROVAL,))
        self.assertEqual("APPROVED", approved.approval_status)


if __name__ == "__main__":
    unittest.main()
