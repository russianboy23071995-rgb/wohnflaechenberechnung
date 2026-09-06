"""Repository-Interfaces (Abstraktionen für die Infrastructure-Schicht)."""

from abc import ABC, abstractmethod
from typing import Optional

from wohnflaechen.domain.entities.building import Building
from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType


class ProjectRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Project]:
        ...

    @abstractmethod
    def list_by_auftrag(self, auftrag_id: int) -> list[Project]:
        ...

    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]:
        ...

    @abstractmethod
    def save(self, project: Project) -> Project:
        ...

    @abstractmethod
    def delete(self, project_id: int) -> None:
        ...


class BuildingRepository(ABC):
    @abstractmethod
    def list_by_project(self, project_id: int) -> list[Building]:
        ...

    @abstractmethod
    def get_by_id(self, building_id: int) -> Optional[Building]:
        ...

    @abstractmethod
    def get_by_prefix(self, project_id: int, room_prefix: str) -> Optional[Building]:
        ...

    @abstractmethod
    def save(self, building: Building) -> Building:
        ...

    @abstractmethod
    def delete(self, building_id: int) -> None:
        ...

    @abstractmethod
    def reorder(self, project_id: int, building_ids: list[int]) -> None:
        ...


class FloorRepository(ABC):
    @abstractmethod
    def list_by_project(self, project_id: int) -> list[Floor]:
        ...

    @abstractmethod
    def get_by_id(self, floor_id: int) -> Optional[Floor]:
        ...

    @abstractmethod
    def save(self, floor: Floor) -> Floor:
        ...

    @abstractmethod
    def delete(self, floor_id: int) -> None:
        ...

    @abstractmethod
    def reorder(self, project_id: int, floor_ids: list[int]) -> None:
        ...


class RoomRepository(ABC):
    @abstractmethod
    def list_by_project(self, project_id: int) -> list[Room]:
        ...

    @abstractmethod
    def get_by_id(self, room_id: int) -> Optional[Room]:
        ...

    @abstractmethod
    def save(self, room: Room) -> Room:
        ...

    @abstractmethod
    def save_many(self, rooms: list[Room]) -> list[Room]:
        ...

    @abstractmethod
    def delete(self, room_id: int) -> None:
        ...

    @abstractmethod
    def restore(self, room: Room) -> Room:
        ...


class TextBlockRepository(ABC):
    @abstractmethod
    def list_by_project(self, project_id: int) -> list[TextBlock]:
        ...

    @abstractmethod
    def get_by_type(self, project_id: int, block_type: TextBlockType) -> Optional[TextBlock]:
        ...

    @abstractmethod
    def save(self, text_block: TextBlock) -> TextBlock:
        ...
