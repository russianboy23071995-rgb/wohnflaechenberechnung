"""Rechnungsverwaltung."""

from datetime import date, datetime
from typing import Optional

from wohnflaechen.domain.entities.invoice import Invoice
from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.infrastructure.database.auftrag_repositories import SQLiteInvoiceRepository


class InvoiceService:
    def __init__(self, invoice_repository: SQLiteInvoiceRepository) -> None:
        self._invoices = invoice_repository

    def get_invoice(self, auftrag_id: int) -> Optional[Invoice]:
        return self._invoices.get_by_auftrag(auftrag_id)

    def list_invoices(self, auftrag_id: int) -> list[Invoice]:
        return self._invoices.list_by_auftrag(auftrag_id)

    def suggest_number(self) -> str:
        year = date.today().year
        count = self._invoices.count_all() + 1
        return f"RE-{year}-{count:03d}"

    def create_from_offer(self, auftrag_id: int, offer: Offer | None) -> Invoice:
        service = offer.service_description if offer else ""
        price = offer.price if offer else 0.0
        return Invoice(
            auftrag_id=auftrag_id,
            number=self.suggest_number(),
            date=date.today(),
            service_description=service,
            price=price,
        )

    def save_invoice(self, invoice: Invoice) -> Invoice:
        if invoice.created_at is None and invoice.id is None:
            invoice.created_at = datetime.now()
        return self._invoices.save(invoice)
