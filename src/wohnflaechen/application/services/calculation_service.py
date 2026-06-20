"""Summenberechnungen für Wohn- und Nutzflächen."""

from dataclasses import dataclass

from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.entities.room import Room


@dataclass
class FloorSummary:
    """Summen pro Geschoss."""

    floor_id: int | None
    floor_name: str
    living_area: float
    usable_area: float


@dataclass
class ProjectSummary:
    """Gesamtsummen eines Projekts."""

    total_living_area: float
    total_usable_area: float
    floor_summaries: list[FloorSummary]


class CalculationService:
    """Berechnet Flächensummen unabhängig von der PDF-Ausgabe."""

    def summarize(
        self,
        rooms: list[Room],
        floors: list[Floor],
    ) -> ProjectSummary:
        floor_lookup = {floor.id: floor for floor in floors}
        floor_summaries: dict[int | None, FloorSummary] = {}

        for room in rooms:
            key = room.floor_id
            if key not in floor_summaries:
                floor_name = "Ohne Geschoss"
                if key is not None and key in floor_lookup:
                    floor_name = floor_lookup[key].name
                floor_summaries[key] = FloorSummary(
                    floor_id=key,
                    floor_name=floor_name,
                    living_area=0.0,
                    usable_area=0.0,
                )

            summary = floor_summaries[key]
            summary.living_area = round(summary.living_area + room.living_area, 2)
            summary.usable_area = round(summary.usable_area + room.usable_area, 2)

        ordered_summaries: list[FloorSummary] = []
        for floor in floors:
            if floor.id in floor_summaries:
                ordered_summaries.append(floor_summaries[floor.id])
        if None in floor_summaries:
            ordered_summaries.append(floor_summaries[None])

        total_living = round(sum(s.living_area for s in ordered_summaries), 2)
        total_usable = round(sum(s.usable_area for s in ordered_summaries), 2)

        return ProjectSummary(
            total_living_area=total_living,
            total_usable_area=total_usable,
            floor_summaries=ordered_summaries,
        )
