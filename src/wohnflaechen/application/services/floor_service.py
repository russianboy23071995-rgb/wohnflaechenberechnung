"""Geschossverwaltung."""

from typing import Optional

from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.repositories.interfaces import FloorRepository


class FloorService:
    """Use Cases für Geschossanlage und Reihenfolge."""

    def __init__(self, floor_repository: FloorRepository) -> None:
        self._floors = floor_repository

    def list_floors(self, project_id: int) -> list[Floor]:
        return self._floors.list_by_project(project_id)

    def get_floor(self, floor_id: int) -> Optional[Floor]:
        return self._floors.get_by_id(floor_id)

    def create_floor(self, project_id: int, name: str) -> Floor:
        existing = self._floors.list_by_project(project_id)
        floor = Floor(
            project_id=project_id,
            name=name.strip(),
            sort_order=len(existing),
        )
        return self._floors.save(floor)

    def update_floor(self, floor: Floor) -> Floor:
        return self._floors.save(floor)

    def delete_floor(self, floor_id: int) -> None:
        self._floors.delete(floor_id)

    def reorder_floors(self, project_id: int, floor_ids: list[int]) -> None:
        self._floors.reorder(project_id, floor_ids)

    def floor_map_by_name(self, project_id: int) -> dict[str, int]:
        return {floor.name: floor.id for floor in self.list_floors(project_id)}
