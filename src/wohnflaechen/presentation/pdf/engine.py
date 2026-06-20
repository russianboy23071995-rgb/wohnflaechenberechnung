"""PDF-Erzeugung mit Jinja2 und WeasyPrint."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from wohnflaechen.application.dto.pdf_document import PdfDocument
from wohnflaechen.presentation.pdf.branding import (
    COMPANY_NAME,
    COMPANY_TAGLINE,
    DOCUMENT_SUBTITLE,
    DOCUMENT_TITLE_FULL,
    DOCUMENT_TITLE_LINE_1,
    DOCUMENT_TITLE_LINE_2,
    FOOTER_EMAIL,
    FOOTER_WEBSITE,
    LOGO_HORIZONTAL,
    LOGO_ICON,
    PREFACE_TITLE,
    STAMP_SIGNATURE,
)
from wohnflaechen.presentation.pdf.formatters import (
    calculation_html,
    name_html,
    paragraphs_html,
    preface_content_html,
)

_PACKAGE_DIR = Path(__file__).parent
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"
_STATIC_DIR = _PACKAGE_DIR / "static"


class PdfEngine:
    """Erzeugt PDF-Dokumente im Corporate Design."""

    def __init__(self, templates_dir: Path | None = None, static_dir: Path | None = None) -> None:
        self._templates_dir = templates_dir or _TEMPLATES_DIR
        self._static_dir = static_dir or _STATIC_DIR
        self._env = Environment(
            loader=FileSystemLoader(self._templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_pdf(self, document: PdfDocument, output_path: Path) -> Path:
        try:
            from weasyprint import HTML
        except OSError as exc:
            raise RuntimeError(
                "PDF-Export benötigt die GTK3-Runtime für WeasyPrint unter Windows. "
                "Anleitung: https://doc.courtbouillon.org/weasyprint/stable/"
                "first_steps.html#windows"
            ) from exc

        html_content = self._render_html(document)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(string=html_content, base_url=str(self._static_dir)).write_pdf(str(output_path))
        return output_path

    def _render_html(self, document: PdfDocument) -> str:
        template = self._env.get_template("document.html")
        floors = []
        page_offset = 2
        for floor in document.floors:
            rooms = []
            for room in floor.rooms:
                rooms.append(
                    {
                        "index": room.index,
                        "name_html": name_html(room.name),
                        "calculation_html": calculation_html(room.calculation),
                        "factor": room.factor,
                        "usable_area": room.usable_area,
                        "living_area": room.living_area,
                    }
                )
            floors.append(
                {
                    "section_index": floor.section_index,
                    "name": floor.name,
                    "rooms": rooms,
                    "sum_living": floor.sum_living,
                    "sum_usable": floor.sum_usable,
                    "page_number": page_offset,
                }
            )
            page_offset += 1

        summary_page_number = page_offset

        return template.render(
            company_name=COMPANY_NAME,
            company_tagline=COMPANY_TAGLINE,
            footer_website=FOOTER_WEBSITE,
            footer_email=FOOTER_EMAIL,
            logo_icon=LOGO_ICON,
            logo_horizontal=LOGO_HORIZONTAL,
            stamp_signature=STAMP_SIGNATURE,
            document_title_full=DOCUMENT_TITLE_FULL,
            document_title_line_1=DOCUMENT_TITLE_LINE_1,
            document_title_line_2=DOCUMENT_TITLE_LINE_2,
            document_subtitle=DOCUMENT_SUBTITLE,
            preface_title=PREFACE_TITLE,
            page_number=1,
            object_name=document.object_name,
            address=document.address,
            object_description_html=paragraphs_html(document.object_description),
            preface_html=preface_content_html(document.preface),
            methodology_html=paragraphs_html(document.methodology),
            special_notes_html=paragraphs_html(document.special_notes),
            liability_html=paragraphs_html(document.liability),
            floors=floors,
            floor_totals=document.floor_totals,
            total_living=document.total_living,
            total_usable=document.total_usable,
            footer_location=document.footer_location,
            footer_date=document.footer_date,
            editor=document.editor,
            summary_page_number=summary_page_number,
        )
