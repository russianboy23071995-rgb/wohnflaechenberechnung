"""PDF-Erzeugung mit Jinja2 und WeasyPrint."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from wohnflaechen.application.dto.pdf_document import PdfDocument
from wohnflaechen.domain.enums.pdf_layout import PdfLayout
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
    bauantrag_calculation_html,
    calculation_html,
    multiline_html,
    name_html,
    paragraphs_html,
    preface_content_html,
)
from wohnflaechen.presentation.paths import pdf_static_dir, pdf_templates_dir
from wohnflaechen.presentation.pdf.weasyprint_support import (
    PdfExportNotAvailableError,
    get_weasyprint_html,
)


class PdfEngine:
    """Erzeugt PDF-Dokumente im Corporate Design."""

    def __init__(self, templates_dir: Path | None = None, static_dir: Path | None = None) -> None:
        self._templates_dir = templates_dir or pdf_templates_dir()
        self._static_dir = static_dir or pdf_static_dir()
        self._env = Environment(
            loader=FileSystemLoader(self._templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_pdf(
        self,
        document: PdfDocument,
        output_path: Path,
        layout: PdfLayout = PdfLayout.STANDARD,
    ) -> Path:
        try:
            HTML = get_weasyprint_html()
        except PdfExportNotAvailableError:
            raise

        html_content = self._render_html(document, layout)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            HTML(string=html_content, base_url=str(self._static_dir)).write_pdf(str(output_path))
        except OSError as exc:
            raise PdfExportNotAvailableError(
                "Beim Schreiben des PDF ist ein Systemfehler aufgetreten "
                "(häufig fehlende GTK-Bibliotheken unter Windows).\n\n"
                f"Technische Details: {exc}"
            ) from exc
        return output_path

    def _render_html(self, document: PdfDocument, layout: PdfLayout) -> str:
        if layout == PdfLayout.BAUANTRAG:
            return self._render_bauantrag_html(document)
        return self._render_standard_html(document)

    def _render_bauantrag_html(self, document: PdfDocument) -> str:
        template = self._env.get_template("document_bauantrag.html")
        living_sections = []
        for section in document.classic_living_sections:
            living_sections.append(
                {
                    "heading": section.heading,
                    "area_column_title": section.area_column_title,
                    "sum_label": section.sum_label,
                    "sum_value": section.sum_value,
                    "rows": [
                        {
                            "number": row.number,
                            "name_html": name_html(row.name),
                            "calculation_html": bauantrag_calculation_html(row.calculation),
                            "area_result": row.area_result,
                        }
                        for row in section.rows
                    ],
                }
            )
        usable_sections = []
        for section in document.classic_usable_sections:
            usable_sections.append(
                {
                    "heading": section.heading,
                    "area_column_title": section.area_column_title,
                    "sum_label": section.sum_label,
                    "sum_value": section.sum_value,
                    "rows": [
                        {
                            "number": row.number,
                            "name_html": name_html(row.name),
                            "calculation_html": bauantrag_calculation_html(row.calculation),
                            "area_result": row.area_result,
                        }
                        for row in section.rows
                    ],
                }
            )
        living_summary = None
        if document.classic_living_summary:
            living_summary = {
                "title": document.classic_living_summary.title,
                "lines": document.classic_living_summary.lines,
                "total_label": document.classic_living_summary.total_label,
                "total_value": document.classic_living_summary.total_value,
            }
        usable_summary = None
        if document.classic_usable_summary:
            usable_summary = {
                "title": document.classic_usable_summary.title,
                "lines": document.classic_usable_summary.lines,
                "total_label": document.classic_usable_summary.total_label,
                "total_value": document.classic_usable_summary.total_value,
            }
        return template.render(
            company_name=COMPANY_NAME,
            object_name=document.object_name,
            address=document.address,
            client_html=multiline_html(document.client),
            measure_html=multiline_html(document.measure_title),
            editor=document.editor or "—",
            footer_location=document.footer_location,
            footer_date=document.footer_date,
            classic_living_sections=living_sections,
            classic_usable_sections=usable_sections,
            classic_living_summary=living_summary,
            classic_usable_summary=usable_summary,
        )

    def _render_standard_html(self, document: PdfDocument) -> str:
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
