"""Erzeugt Ausgabe-Dokumente aus Projektdaten – ohne PDF-Abhängigkeit."""

from datetime import datetime

from wohnflaechen.application.dto.pdf_document import (
    PdfDocument,
    PdfFloorSection,
    PdfFloorTotal,
    PdfRoomRow,
)
from wohnflaechen.application.services.calculation_service import CalculationService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.project_service import ProjectService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor
from wohnflaechen.domain.enums.text_block_type import TextBlockType


def _format_area_cell(value: float) -> str:
    if value == 0:
        return "-"
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_column(value: float) -> str:
    """Spaltenwert – leer wenn keine Fläche vorhanden."""
    if value == 0:
        return ""
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_total(value: float) -> str:
    if value == 0:
        return "00,00 m²"
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_summary_display(value: float) -> str:
    """Zusammenfassung – Wert immer mit zwei Nachkommastellen."""
    return f"{value:.2f} m²".replace(".", ",")


def _format_factor(factor: Factor) -> str:
    return factor.value.replace(" ", "")


def _room_living_area(room: Room) -> float:
    if room.area_type == AreaType.WOHNFLAECHE:
        return room.credited_area
    return 0.0


def _room_usable_area(room: Room) -> float:
    if room.area_type == AreaType.NUTZFLAECHE:
        return room.credited_area
    return 0.0


class DocumentExportService:
    """Baut PdfDocument aus gespeicherten Projektinformationen."""

    DEFAULT_LOCATION = "Hamburg"

    def __init__(
        self,
        project_service: ProjectService,
        floor_service: FloorService,
        room_service: RoomService,
        text_block_service: TextBlockService,
        calculation_service: CalculationService,
    ) -> None:
        self._projects = project_service
        self._floors = floor_service
        self._rooms = room_service
        self._text_blocks = text_block_service
        self._calculation = calculation_service

    def build_document(self, project_id: int) -> PdfDocument:
        project = self._projects.get_project(project_id)
        if not project:
            raise ValueError(f"Projekt {project_id} nicht gefunden.")

        floors = self._floors.list_floors(project_id)
        rooms = self._rooms.list_rooms(project_id)
        summary = self._calculation.summarize(rooms, floors)

        floor_sections: list[PdfFloorSection] = []
        floor_totals: list[PdfFloorTotal] = []

        rooms_by_floor: dict[int | None, list[Room]] = {}
        for room in rooms:
            rooms_by_floor.setdefault(room.floor_id, []).append(room)

        for section_index, floor in enumerate(floors, start=1):
            floor_rooms = rooms_by_floor.get(floor.id, [])
            rows = self._build_room_rows(floor_rooms)

            floor_summary = next(
                (s for s in summary.floor_summaries if s.floor_id == floor.id),
                None,
            )
            living_sum = floor_summary.living_area if floor_summary else 0.0
            usable_sum = floor_summary.usable_area if floor_summary else 0.0

            floor_sections.append(
                PdfFloorSection(
                    section_index=section_index,
                    name=floor.name,
                    rooms=rows,
                    sum_living=_format_area_column(living_sum),
                    sum_usable=_format_area_column(usable_sum),
                )
            )
            floor_totals.append(
                PdfFloorTotal(
                    name=floor.name,
                    living_area=_format_area_summary_display(living_sum),
                    usable_area=_format_area_summary_display(usable_sum),
                )
            )

        unassigned = rooms_by_floor.get(None, [])
        if unassigned:
            rows = self._build_room_rows(unassigned)
            living_sum = round(sum(_room_living_area(r) for r in unassigned), 2)
            usable_sum = round(sum(_room_usable_area(r) for r in unassigned), 2)
            floor_sections.append(
                PdfFloorSection(
                    section_index=len(floor_sections) + 1,
                    name="Ohne Geschoss",
                    rooms=rows,
                    sum_living=_format_area_column(living_sum),
                    sum_usable=_format_area_column(usable_sum),
                )
            )
            floor_totals.append(
                PdfFloorTotal(
                    name="Ohne Geschoss",
                    living_area=_format_area_summary_display(living_sum),
                    usable_area=_format_area_summary_display(usable_sum),
                )
            )

        footer_date = ""
        if project.created_at:
            footer_date = project.created_at.strftime("%d.%m.%Y")
        else:
            footer_date = datetime.now().strftime("%d.%m.%Y")

        return PdfDocument(
            object_name=project.object_name or project.name,
            address=project.address,
            object_description=self._text(
                project_id, TextBlockType.OBJECT_DESCRIPTION
            ),
            preface=self._text(project_id, TextBlockType.PREFACE),
            methodology=self._text(project_id, TextBlockType.METHODOLOGY),
            liability=self._text(project_id, TextBlockType.LIABILITY),
            special_notes=self._text(project_id, TextBlockType.SPECIAL_NOTES),
            floors=floor_sections,
            total_living=_format_area_total(summary.total_living_area),
            total_usable=_format_area_total(summary.total_usable_area),
            floor_totals=floor_totals,
            footer_location=self.DEFAULT_LOCATION,
            footer_date=footer_date,
            editor=project.editor,
            client=project.client,
        )

    def _text(self, project_id: int, block_type: TextBlockType) -> str:
        block = self._text_blocks.get_text_block(project_id, block_type)
        return block.content.strip()

    def _build_room_rows(self, rooms: list[Room]) -> list[PdfRoomRow]:
        rows: list[PdfRoomRow] = []
        for index, room in enumerate(rooms, start=1):
            rows.append(
                PdfRoomRow(
                    index=f"{index:02d}",
                    name=room.name,
                    calculation=room.calculation_path,
                    factor=_format_factor(room.factor),
                    usable_area=_format_area_cell(_room_usable_area(room)),
                    living_area=_format_area_cell(_room_living_area(room)),
                )
            )
        return rows
