from __future__ import annotations

import unittest
from decimal import Decimal

from atlas_runtime.commercial_payment import CommercialLedger, InvoiceStatus


class CommercialPaymentTests(unittest.TestCase):
    def test_billing_readiness_preserves_px_project_contract_and_milestone_lineage(self) -> None:
        ledger = CommercialLedger("2026_PX00011_APIS", project_id="2026_PX00011_APIS", contract_ref="CTR-001")
        ledger.register_entitlement("ENT-001", milestone_id="M-001", amount="100000", currency="USD", evidence_ref="SP://acceptance")

        entitlement = ledger.entitlements["ENT-001"]
        self.assertEqual("2026_PX00011_APIS", entitlement.px_id)
        self.assertEqual("2026_PX00011_APIS", entitlement.project_id)
        self.assertEqual("CTR-001", entitlement.contract_ref)
        self.assertEqual("M-001", entitlement.milestone_id)

    def test_invoice_requires_evidenced_entitlement_and_approval(self) -> None:
        ledger = CommercialLedger("2026_PX00011_APIS", project_id="2026_PX00011_APIS", contract_ref="CTR-001")
        ledger.register_entitlement("ENT-001", milestone_id="M-001", amount="100000", currency="USD", evidence_ref="SP://acceptance")

        with self.assertRaises(ValueError):
            ledger.issue_invoice("INV-001", entitlement_id="ENT-001", due_date="2027-01-31", approved=False, submission_ref="SP://invoice")

        ledger.issue_invoice("INV-001", entitlement_id="ENT-001", due_date="2027-01-31", approved=True, submission_ref="SP://invoice")
        self.assertEqual(InvoiceStatus.ISSUED, ledger.invoices["INV-001"].status)

    def test_partial_payments_reconcile_against_invoice(self) -> None:
        ledger = CommercialLedger("2026_PX00011_APIS", project_id="2026_PX00011_APIS", contract_ref="CTR-001")
        ledger.register_entitlement("ENT-001", milestone_id="M-001", amount="100000", currency="USD", evidence_ref="SP://acceptance")
        ledger.issue_invoice("INV-001", entitlement_id="ENT-001", due_date="2027-01-31", approved=True, submission_ref="SP://invoice")

        ledger.record_payment("PAY-001", invoice_id="INV-001", amount="40000", evidence_ref="SP://bank-1")
        self.assertEqual(Decimal("60000"), ledger.outstanding_amount("INV-001"))
        self.assertEqual(InvoiceStatus.PARTIALLY_PAID, ledger.invoices["INV-001"].status)

        ledger.record_payment("PAY-002", invoice_id="INV-001", amount="60000", evidence_ref="SP://bank-2")
        self.assertEqual(Decimal("0"), ledger.outstanding_amount("INV-001"))
        self.assertEqual(InvoiceStatus.PAID, ledger.invoices["INV-001"].status)

    def test_overpayment_is_rejected(self) -> None:
        ledger = CommercialLedger("2026_PX00011_APIS", project_id="2026_PX00011_APIS", contract_ref="CTR-001")
        ledger.register_entitlement("ENT-001", milestone_id="M-001", amount="100", currency="USD", evidence_ref="SP://acceptance")
        ledger.issue_invoice("INV-001", entitlement_id="ENT-001", due_date="2027-01-31", approved=True, submission_ref="SP://invoice")

        with self.assertRaises(ValueError):
            ledger.record_payment("PAY-001", invoice_id="INV-001", amount="101", evidence_ref="SP://bank")

    def test_overdue_invoices_are_exposed_for_escalation(self) -> None:
        ledger = CommercialLedger("2026_PX00011_APIS", project_id="2026_PX00011_APIS", contract_ref="CTR-001")
        ledger.register_entitlement("ENT-001", milestone_id="M-001", amount="100", currency="USD", evidence_ref="SP://acceptance")
        ledger.issue_invoice("INV-001", entitlement_id="ENT-001", due_date="2027-01-31", approved=True, submission_ref="SP://invoice")

        self.assertEqual(("INV-001",), ledger.overdue_invoices(as_of="2027-02-01"))


if __name__ == "__main__":
    unittest.main()
