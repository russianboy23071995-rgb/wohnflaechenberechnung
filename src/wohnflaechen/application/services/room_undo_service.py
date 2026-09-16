"""Rückgängig-Stapel für Raumänderungen."""

from copy import copy

from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.repositories.interfaces import RoomRepository


def _clone_room(room: Room) -> Room:
    return Room(
        id=room.id,
        project_id=room.project_id,
        floor_id=room.floor_id,
        name=room.name,
        number=room.number,
        raw_area=room.raw_area,
        area_type=copy(room.area_type),
        factor=copy(room.factor),
        calculation_path=room.calculation_path,
        note=room.note,
    )


class RoomUndoService:
    def __init__(self, room_repository: RoomRepository, max_depth: int = 40) -> None:
        self._rooms = room_repository
        self._stacks: dict[int, list[list[Room]]] = {}
        self._max_depth = max_depth

    def record(self, project_id: int) -> None:
        rooms = self._rooms.list_by_project(project_id)
        snapshot = [_clone_room(room) for room in rooms]
        stack = self._stacks.setdefault(project_id, [])
        stack.append(snapshot)
        if len(stack) > self._max_depth:
            stack.pop(0)

    def can_undo(self, project_id: int) -> bool:
        return bool(self._stacks.get(project_id))

    def undo(self, project_id: int) -> bool:
        stack = self._stacks.get(project_id)
        if not stack:
            return False
        snapshot = stack.pop()
        current = self._rooms.list_by_project(project_id)
        current_ids = {room.id for room in current if room.id is not None}
        snapshot_ids = {room.id for room in snapshot if room.id is not None}

        for room_id in current_ids - snapshot_ids:
            self._rooms.delete(room_id)

        for room in snapshot:
            if room.id is None:
                continue
            if room.id in current_ids:
                self._rooms.save(room)
            else:
                self._rooms.restore(room)

        return True

    def clear(self, project_id: int) -> None:
        self._stacks.pop(project_id, None)
