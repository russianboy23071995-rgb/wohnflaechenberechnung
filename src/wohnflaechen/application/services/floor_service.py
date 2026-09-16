"""Geschossverwaltung."""

from typing import Optional

from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.repositories.interfaces import FloorRepository


class FloorService:
    """Use Cases für Geschossanlage und Reihenfolge."""

    def __init__(self, floor_repository: FloorRepository) -> None:
        self._floors = floor_repository

    def list_floors(
        self,
        project_id: int,
        building_id: int | None | str = "all",
    ) -> list[Floor]:
        floors = self._floors.list_by_project(project_id)
        if building_id == "all":
            return floors
        return [floor for floor in floors if floor.building_id == building_id]

    def get_floor(self, floor_id: int) -> Optional[Floor]:
        return self._floors.get_by_id(floor_id)

    def create_floor(
        self,
        project_id: int,
        name: str,
        building_id: int | None = None,
    ) -> Floor:
        if building_id is not None:
            existing = [
                floor
                for floor in self._floors.list_by_project(project_id)
                if floor.building_id == building_id
            ]
        else:
            existing = [
                floor
                for floor in self._floors.list_by_project(project_id)
                if floor.building_id is None
            ]
        floor = Floor(
            project_id=project_id,
            building_id=building_id,
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
