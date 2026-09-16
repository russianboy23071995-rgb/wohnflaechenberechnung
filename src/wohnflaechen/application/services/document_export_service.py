"""Erzeugt Ausgabe-Dokumente aus Projektdaten – ohne PDF-Abhängigkeit."""

from datetime import datetime

from wohnflaechen.application.dto.pdf_document import (
    PdfClassicSection,
    PdfClassicSummary,
    PdfClassicTableRow,
    PdfDocument,
    PdfFloorSection,
    PdfFloorTotal,
    PdfRoomRow,
)
from wohnflaechen.application.services.building_service import BuildingService
from wohnflaechen.application.services.calculation_service import CalculationService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.preface_service import preface_block_type
from wohnflaechen.application.services.project_service import ProjectService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.domain.entities.building import Building
from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor
from wohnflaechen.domain.enums.text_block_type import TextBlockType


def _format_area_cell(value: float) -> str:
    if value == 0:
        return "-"
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_column(value: float) -> str:
    if value == 0:
        return ""
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_total(value: float) -> str:
    if value == 0:
        return "00,00 m²"
    return f"{value:.2f} m²".replace(".", ",")


def _format_area_summary_display(value: float) -> str:
    return f"{value:.2f} m²".replace(".", ",")


def _format_classic_area(value: float) -> str:
    if value == 0:
        return "-"
    return f"= {_format_area_summary_display(value)}"


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
        building_service: BuildingService,
        room_service: RoomService,
        text_block_service: TextBlockService,
        calculation_service: CalculationService,
    ) -> None:
        self._projects = project_service
        self._floors = floor_service
        self._buildings = building_service
        self._rooms = room_service
        self._text_blocks = text_block_service
        self._calculation = calculation_service

    def build_document(self, project_id: int) -> PdfDocument:
        project = self._projects.get_project(project_id)
        if not project:
            raise ValueError(f"Projekt {project_id} nicht gefunden.")

        floors = self._floors.list_floors(project_id)
        buildings = self._buildings.list_buildings(project_id)
        rooms = self._rooms.list_rooms(project_id)
        summary = self._calculation.summarize(rooms, floors)

        rooms_by_floor: dict[int | None, list[Room]] = {}
        for room in rooms:
            rooms_by_floor.setdefault(room.floor_id, []).append(room)

        floor_sections, floor_totals = self._build_standard_sections(
            floors, rooms_by_floor, summary
        )
        classic_living, classic_usable, living_summary, usable_summary = self._build_classic_sections(
            floors, buildings, rooms_by_floor
        )

        footer_date = ""
        if project.created_at:
            footer_date = project.created_at.strftime("%d.%m.%Y")
        else:
            footer_date = datetime.now().strftime("%d.%m.%Y")

        return PdfDocument(
            object_name=project.object_name or project.name,
            address=project.address,
            client=project.client,
            measure_title=self._text(project_id, TextBlockType.MEASURE),
            object_description=self._text(project_id, TextBlockType.OBJECT_DESCRIPTION),
            preface=self._preface_text(project),
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
            classic_living_sections=classic_living,
            classic_usable_sections=classic_usable,
            classic_living_summary=living_summary,
            classic_usable_summary=usable_summary,
        )

    def _build_standard_sections(self, floors, rooms_by_floor, summary):
        floor_sections: list[PdfFloorSection] = []
        floor_totals: list[PdfFloorTotal] = []

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
            living_sum = round(sum(_room_living_area(r) for r in unassigned), 2)
            usable_sum = round(sum(_room_usable_area(r) for r in unassigned), 2)
            floor_sections.append(
                PdfFloorSection(
                    section_index=len(floor_sections) + 1,
                    name="Ohne Geschoss",
                    rooms=self._build_room_rows(unassigned),
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
        return floor_sections, floor_totals

    def _build_classic_sections(
        self,
        floors: list[Floor],
        buildings: list[Building],
        rooms_by_floor: dict[int | None, list[Room]],
    ):
        living_sections: list[PdfClassicSection] = []
        usable_sections: list[PdfClassicSection] = []
        living_summary_lines: list[tuple[str, str]] = []
        usable_summary_lines: list[tuple[str, str]] = []
        total_living = 0.0
        total_usable = 0.0

        groups = self._floor_groups(floors, buildings)
        multi_building = len(buildings) > 0

        for building, group_floors in groups:
            for floor in group_floors:
                floor_rooms = rooms_by_floor.get(floor.id, [])
                living_rooms = [room for room in floor_rooms if room.area_type == AreaType.WOHNFLAECHE]
                usable_rooms = [room for room in floor_rooms if room.area_type == AreaType.NUTZFLAECHE]

                living_sum = round(sum(_room_living_area(room) for room in living_rooms), 2)
                usable_sum = round(sum(_room_usable_area(room) for room in usable_rooms), 2)

                if living_rooms:
                    heading = self._classic_heading("Wohnflächenberechnung", floor.name, building, multi_building)
                    living_sections.append(
                        PdfClassicSection(
                            heading=heading,
                            area_column_title="Wohnfläche",
                            rows=self._build_classic_rows(living_rooms, AreaType.WOHNFLAECHE),
                            sum_label=f"Summe Wohnflächenberechnung {floor.name}",
                            sum_value=_format_classic_area(living_sum),
                        )
                    )
                    living_summary_lines.append(
                        (f"Summe Wohnfläche {floor.name}:", _format_classic_area(living_sum))
                    )
                    total_living = round(total_living + living_sum, 2)

                if usable_rooms:
                    heading = self._classic_heading(
                        "Nutzflächenberechnung",
                        floor.name,
                        building,
                        multi_building,
                    )
                    usable_sections.append(
                        PdfClassicSection(
                            heading=heading,
                            area_column_title="Nutzfläche",
                            rows=self._build_classic_rows(usable_rooms, AreaType.NUTZFLAECHE),
                            sum_label=f"Summe Nutzfläche {floor.name}",
                            sum_value=_format_classic_area(usable_sum),
                        )
                    )
                    usable_summary_lines.append(
                        (f"Summe Nutzfläche {floor.name}:", _format_classic_area(usable_sum))
                    )
                    total_usable = round(total_usable + usable_sum, 2)

        living_summary = PdfClassicSummary(
            title="Zusammenfassung der Wohnflächenberechnung",
            lines=living_summary_lines,
            total_label="Summe Wohnfläche Insgesamt:",
            total_value=_format_classic_area(total_living),
        )
        usable_summary = PdfClassicSummary(
            title="Zusammenfassung der Nutzfläche",
            lines=usable_summary_lines,
            total_label="Summe Nutzfläche Insgesamt:",
            total_value=_format_classic_area(total_usable),
        )
        return living_sections, usable_sections, living_summary, usable_summary

    def _floor_groups(
        self,
        floors: list[Floor],
        buildings: list[Building],
    ) -> list[tuple[Building | None, list[Floor]]]:
        if not buildings:
            return [(None, floors)]
        groups: list[tuple[Building | None, list[Floor]]] = []
        for building in buildings:
            group = [floor for floor in floors if floor.building_id == building.id]
            if group:
                groups.append((building, group))
        unassigned = [floor for floor in floors if floor.building_id is None]
        if unassigned:
            groups.append((None, unassigned))
        return groups

    def _classic_heading(
        self,
        prefix: str,
        floor_name: str,
        building: Building | None,
        multi_building: bool,
    ) -> str:
        if multi_building and building:
            return f"{prefix} – {building.name} – {floor_name}"
        return f"{prefix} – {floor_name}"

    def _build_classic_rows(self, rooms: list[Room], area_type: AreaType) -> list[PdfClassicTableRow]:
        rows: list[PdfClassicTableRow] = []
        for room in rooms:
            number = room.number.strip()
            if number and not number.endswith(":"):
                number = f"{number}:"
            area_value = _room_living_area(room) if area_type == AreaType.WOHNFLAECHE else _room_usable_area(room)
            rows.append(
                PdfClassicTableRow(
                    number=number,
                    name=room.name,
                    calculation=room.calculation_path,
                    area_result=_format_classic_area(area_value),
                )
            )
        return rows

    def _preface_text(self, project) -> str:
        if project.id is None:
            return ""
        variant = self._text(project.id, preface_block_type(project.measurement_on_site))
        if variant:
            return variant
        return self._text(project.id, TextBlockType.PREFACE)

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
