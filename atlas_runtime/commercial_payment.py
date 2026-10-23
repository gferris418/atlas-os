from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum


class InvoiceStatus(str, Enum):
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"


@dataclass(frozen=True)
class Entitlement:
    entitlement_id: str
    px_id: str
    project_id: str
    contract_ref: str
    milestone_id: str
    amount: Decimal
    currency: str
    evidence_ref: str


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    entitlement_id: str
    due_date: date
    submission_ref: str
    status: InvoiceStatus = InvoiceStatus.ISSUED


@dataclass(frozen=True)
class Payment:
    payment_id: str
    invoice_id: str
    amount: Decimal
    evidence_ref: str


def _positive_amount(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("amount must be numeric") from exc
    if amount <= 0:
        raise ValueError("amount must be positive")
    return amount


@dataclass
class CommercialLedger:
    px_id: str
    project_id: str
    contract_ref: str
    entitlements: dict[str, Entitlement] = field(default_factory=dict)
    invoices: dict[str, Invoice] = field(default_factory=dict)
    payments: dict[str, Payment] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.px_id, self.project_id, self.contract_ref)):
            raise ValueError("px_id, project_id, and contract_ref must be non-empty")

    def register_entitlement(
        self,
        entitlement_id: str,
        *,
        milestone_id: str,
        amount: str,
        currency: str,
        evidence_ref: str,
    ) -> None:
        if entitlement_id in self.entitlements:
            raise ValueError(f"entitlement {entitlement_id} already exists")
        if not all(value.strip() for value in (entitlement_id, milestone_id, currency, evidence_ref)):
            raise ValueError("entitlement fields must be non-empty")
        self.entitlements[entitlement_id] = Entitlement(
            entitlement_id,
            self.px_id,
            self.project_id,
            self.contract_ref,
            milestone_id,
            _positive_amount(amount),
            currency,
            evidence_ref,
        )

    def issue_invoice(
        self,
        invoice_id: str,
        *,
        entitlement_id: str,
        due_date: str,
        approved: bool,
        submission_ref: str,
    ) -> None:
        if not approved:
            raise ValueError("ATLAS approval is required to issue an invoice")
        if invoice_id in self.invoices:
            raise ValueError(f"invoice {invoice_id} already exists")
        if entitlement_id not in self.entitlements:
            raise ValueError(f"unknown entitlement {entitlement_id}")
        if not invoice_id.strip() or not submission_ref.strip():
            raise ValueError("invoice_id and submission_ref must be non-empty")
        parsed_due_date = date.fromisoformat(due_date)
        self.invoices[invoice_id] = Invoice(invoice_id, entitlement_id, parsed_due_date, submission_ref)

    def invoice_amount(self, invoice_id: str) -> Decimal:
        invoice = self.invoices[invoice_id]
        return self.entitlements[invoice.entitlement_id].amount

    def paid_amount(self, invoice_id: str) -> Decimal:
        return sum(
            (payment.amount for payment in self.payments.values() if payment.invoice_id == invoice_id),
            start=Decimal("0"),
        )

    def outstanding_amount(self, invoice_id: str) -> Decimal:
        return self.invoice_amount(invoice_id) - self.paid_amount(invoice_id)

    def record_payment(self, payment_id: str, *, invoice_id: str, amount: str, evidence_ref: str) -> None:
        if payment_id in self.payments:
            raise ValueError(f"payment {payment_id} already exists")
        if invoice_id not in self.invoices:
            raise ValueError(f"unknown invoice {invoice_id}")
        if not payment_id.strip() or not evidence_ref.strip():
            raise ValueError("payment_id and evidence_ref must be non-empty")
        payment_amount = _positive_amount(amount)
        if payment_amount > self.outstanding_amount(invoice_id):
            raise ValueError("payment exceeds outstanding invoice amount")
        self.payments[payment_id] = Payment(payment_id, invoice_id, payment_amount, evidence_ref)
        outstanding = self.outstanding_amount(invoice_id)
        status = InvoiceStatus.PAID if outstanding == 0 else InvoiceStatus.PARTIALLY_PAID
        self.invoices[invoice_id] = replace(self.invoices[invoice_id], status=status)

    def overdue_invoices(self, *, as_of: str) -> tuple[str, ...]:
        as_of_date = date.fromisoformat(as_of)
        return tuple(
            invoice_id
            for invoice_id, invoice in self.invoices.items()
            if invoice.status is not InvoiceStatus.PAID and invoice.due_date < as_of_date
        )


__all__ = ["CommercialLedger", "Entitlement", "Invoice", "InvoiceStatus", "Payment"]
