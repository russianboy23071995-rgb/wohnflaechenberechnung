"""Gebäudeverwaltung – mehrere Häuser pro Projekt."""

from typing import Optional

from wohnflaechen.domain.entities.building import Building
from wohnflaechen.domain.repositories.interfaces import BuildingRepository
from wohnflaechen.infrastructure.data_import.room_prefix import DEFAULT_BUILDING_NAMES


class BuildingService:
    def __init__(self, building_repository: BuildingRepository) -> None:
        self._buildings = building_repository

    def list_buildings(self, project_id: int) -> list[Building]:
        return self._buildings.list_by_project(project_id)

    def get_building(self, building_id: int) -> Optional[Building]:
        return self._buildings.get_by_id(building_id)

    def create_building(
        self,
        project_id: int,
        name: str,
        room_prefix: str = "",
    ) -> Building:
        existing = self._buildings.list_by_project(project_id)
        building = Building(
            project_id=project_id,
            name=name.strip(),
            room_prefix=room_prefix.strip().upper(),
            sort_order=len(existing),
        )
        return self._buildings.save(building)

    def ensure_building_for_prefix(self, project_id: int, room_prefix: str) -> Building:
        prefix = room_prefix.strip().upper()
        existing = self._buildings.get_by_prefix(project_id, prefix)
        if existing:
            return existing
        default_name = DEFAULT_BUILDING_NAMES.get(prefix, f"Haus ({prefix})")
        return self.create_building(project_id, default_name, prefix)

    def update_building(self, building: Building) -> Building:
        return self._buildings.save(building)

    def delete_building(self, building_id: int) -> None:
        self._buildings.delete(building_id)

    def reorder_buildings(self, project_id: int, building_ids: list[int]) -> None:
        self._buildings.reorder(project_id, building_ids)
