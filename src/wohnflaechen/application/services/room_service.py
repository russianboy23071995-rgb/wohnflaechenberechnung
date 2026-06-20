"""Raumverwaltung."""

from typing import Optional

from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.repositories.interfaces import RoomRepository


class RoomService:
    """Use Cases für den Raum-Pool."""

    def __init__(self, room_repository: RoomRepository) -> None:
        self._rooms = room_repository

    def list_rooms(self, project_id: int) -> list[Room]:
        return self._rooms.list_by_project(project_id)

    def get_room(self, room_id: int) -> Optional[Room]:
        return self._rooms.get_by_id(room_id)

    def save_room(self, room: Room) -> Room:
        return self._rooms.save(room)

    def save_rooms(self, rooms: list[Room]) -> list[Room]:
        return self._rooms.save_many(rooms)

    def delete_room(self, room_id: int) -> None:
        self._rooms.delete(room_id)

    def create_room(self, project_id: int) -> Room:
        room = Room(project_id=project_id)
        return self._rooms.save(room)

    def assign_floor(self, room_ids: list[int], floor_id: int | None) -> None:
        for room_id in room_ids:
            room = self._rooms.get_by_id(room_id)
            if room is None:
                continue
            room.floor_id = floor_id
            self._rooms.save(room)

    def set_area_type_bulk(self, room_ids: list[int], area_type: AreaType) -> None:
        for room_id in room_ids:
            room = self._rooms.get_by_id(room_id)
            if room is None:
                continue
            room.area_type = area_type
            self._rooms.save(room)
