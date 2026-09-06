"""PDF für Angebote und Rechnungen (Platzhalter bis Vorlagen geliefert)."""

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.invoice import Invoice
from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.presentation.pdf.branding import COMPANY_NAME, FOOTER_EMAIL, FOOTER_WEBSITE
from wohnflaechen.presentation.pdf.weasyprint_support import get_weasyprint_html
from wohnflaechen.presentation.paths import pdf_templates_dir, pdf_static_dir


@dataclass
class CommercialDocumentContext:
    document_title: str
    document_number_label: str
    document_number: str
    document_date: str
    auftrag: Auftrag
    service_description: str
    price_formatted: str
    notes: str


class CommercialPdfEngine:
    """Erzeugt Angebots- und Rechnungs-PDFs."""

    def __init__(self, templates_dir: Path | None = None, static_dir: Path | None = None) -> None:
        self._templates_dir = templates_dir or pdf_templates_dir()
        self._static_dir = static_dir or pdf_static_dir()
        self._env = Environment(
            loader=FileSystemLoader(self._templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_offer(self, auftrag: Auftrag, offer: Offer, output_path: Path) -> Path:
        ctx = self._build_context(
            document_title="Angebot",
            number_label="Angebotsnummer",
            number=offer.number,
            date_str=self._format_date(offer.date),
            auftrag=auftrag,
            service=offer.service_description,
            price=offer.price,
            notes=offer.notes,
        )
        return self._render("commercial_document.html", ctx, output_path)

    def render_invoice(self, auftrag: Auftrag, invoice: Invoice, output_path: Path) -> Path:
        ctx = self._build_context(
            document_title="Rechnung",
            number_label="Rechnungsnummer",
            number=invoice.number,
            date_str=self._format_date(invoice.date),
            auftrag=auftrag,
            service=invoice.service_description,
            price=invoice.price,
            notes=invoice.notes,
        )
        return self._render("commercial_document.html", ctx, output_path)

    def _build_context(
        self,
        document_title: str,
        number_label: str,
        number: str,
        date_str: str,
        auftrag: Auftrag,
        service: str,
        price: float,
        notes: str,
    ) -> dict:
        return {
            "company_name": COMPANY_NAME,
            "footer_website": FOOTER_WEBSITE,
            "footer_email": FOOTER_EMAIL,
            "document_title": document_title,
            "document_number_label": number_label,
            "document_number": number,
            "document_date": date_str,
            "client_name": auftrag.client_name,
            "client_address": auftrag.client_address,
            "client_email": auftrag.client_email,
            "client_phone": auftrag.client_phone,
            "object_name": auftrag.object_name,
            "object_address": auftrag.object_address,
            "editor": auftrag.editor,
            "service_description": service,
            "price_formatted": f"{price:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", "."),
            "notes": notes,
            "placeholder_notice": (
                "Dieses Layout ist ein Platzhalter. Ihre finale Vorlage wird "
                "später eingebunden."
            ),
        }

    def _format_date(self, value) -> str:
        if not value:
            return ""
        return value.strftime("%d.%m.%Y")

    def _render(self, template_name: str, context: dict, output_path: Path) -> Path:
        HTML = get_weasyprint_html()
        html = self._env.get_template(template_name).render(**context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html, base_url=str(self._static_dir)).write_pdf(str(output_path))
        return output_path
