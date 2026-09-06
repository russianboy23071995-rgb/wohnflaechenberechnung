"""SQLite-Implementierung der Repository-Interfaces."""

from datetime import date, datetime
from typing import Optional

from wohnflaechen.domain.entities.building import Building
from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.domain.repositories.interfaces import (
    BuildingRepository,
    FloorRepository,
    ProjectRepository,
    RoomRepository,
    TextBlockRepository,
)
from wohnflaechen.infrastructure.database.connection import DatabaseConnection


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


class SQLiteProjectRepository(ProjectRepository):
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_all(self) -> list[Project]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_project(row) for row in rows]

    def list_by_auftrag(self, auftrag_id: int) -> list[Project]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM projects WHERE auftrag_id = ? ORDER BY created_at DESC",
            (auftrag_id,),
        ).fetchall()
        return [self._row_to_project(row) for row in rows]

    def get_by_id(self, project_id: int) -> Optional[Project]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return self._row_to_project(row) if row else None

    def save(self, project: Project) -> Project:
        conn = self._connection.connect()
        created_at = project.created_at or datetime.now()
        measurement_date = (
            project.measurement_date.isoformat() if project.measurement_date else None
        )
        measurement_on_site = 1 if project.measurement_on_site else 0

        if project.id is None:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    auftrag_id, name, object_name, address, client, editor,
                    measurement_date, measurement_on_site, measurement_note,
                    created_at, notes, file_path, completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.auftrag_id,
                    project.name,
                    project.object_name,
                    project.address,
                    project.client,
                    project.editor,
                    measurement_date,
                    measurement_on_site,
                    project.measurement_note,
                    created_at.isoformat(),
                    project.notes,
                    project.file_path,
                    1 if project.completed else 0,
                ),
            )
            project.id = cursor.lastrowid
            project.created_at = created_at
        else:
            conn.execute(
                """
                UPDATE projects SET
                    auftrag_id = ?, name = ?, object_name = ?, address = ?, client = ?, editor = ?,
                    measurement_date = ?, measurement_on_site = ?, measurement_note = ?,
                    notes = ?, file_path = ?, completed = ?
                WHERE id = ?
                """,
                (
                    project.auftrag_id,
                    project.name,
                    project.object_name,
                    project.address,
                    project.client,
                    project.editor,
                    measurement_date,
                    measurement_on_site,
                    project.measurement_note,
                    project.notes,
                    project.file_path,
                    1 if project.completed else 0,
                    project.id,
                ),
            )
            project.created_at = created_at

        self._connection.commit()
        return project

    def delete(self, project_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self._connection.commit()

    def _row_to_project(self, row) -> Project:
        measurement_on_site = True
        if "measurement_on_site" in row.keys():
            measurement_on_site = bool(row["measurement_on_site"])
        elif not row["measurement_date"]:
            measurement_on_site = False

        auftrag_id = row["auftrag_id"] if "auftrag_id" in row.keys() else None
        return Project(
            id=row["id"],
            auftrag_id=auftrag_id,
            name=row["name"],
            object_name=row["object_name"],
            address=row["address"],
            client=row["client"],
            editor=row["editor"],
            measurement_date=_parse_date(row["measurement_date"]),
            measurement_on_site=measurement_on_site,
            measurement_note=row["measurement_note"],
            created_at=_parse_datetime(row["created_at"]),
            notes=row["notes"],
            file_path=row["file_path"],
            completed=bool(row["completed"]) if "completed" in row.keys() else False,
        )


class SQLiteBuildingRepository(BuildingRepository):
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_by_project(self, project_id: int) -> list[Building]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM buildings WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        ).fetchall()
        return [self._row_to_building(row) for row in rows]

    def get_by_id(self, building_id: int) -> Optional[Building]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM buildings WHERE id = ?", (building_id,)).fetchone()
        return self._row_to_building(row) if row else None

    def get_by_prefix(self, project_id: int, room_prefix: str) -> Optional[Building]:
        conn = self._connection.connect()
        row = conn.execute(
            "SELECT * FROM buildings WHERE project_id = ? AND room_prefix = ?",
            (project_id, room_prefix.upper()),
        ).fetchone()
        return self._row_to_building(row) if row else None

    def save(self, building: Building) -> Building:
        conn = self._connection.connect()
        if building.id is None:
            cursor = conn.execute(
                """
                INSERT INTO buildings (project_id, name, room_prefix, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (
                    building.project_id,
                    building.name,
                    building.room_prefix.upper(),
                    building.sort_order,
                ),
            )
            building.id = cursor.lastrowid
        else:
            conn.execute(
                """
                UPDATE buildings SET name = ?, room_prefix = ?, sort_order = ?
                WHERE id = ?
                """,
                (building.name, building.room_prefix.upper(), building.sort_order, building.id),
            )
        self._connection.commit()
        return building

    def delete(self, building_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("UPDATE floors SET building_id = NULL WHERE building_id = ?", (building_id,))
        conn.execute("UPDATE rooms SET building_id = NULL WHERE building_id = ?", (building_id,))
        conn.execute("DELETE FROM buildings WHERE id = ?", (building_id,))
        self._connection.commit()

    def reorder(self, project_id: int, building_ids: list[int]) -> None:
        conn = self._connection.connect()
        for index, building_id in enumerate(building_ids):
            conn.execute(
                "UPDATE buildings SET sort_order = ? WHERE id = ? AND project_id = ?",
                (index, building_id, project_id),
            )
        self._connection.commit()

    def _row_to_building(self, row) -> Building:
        return Building(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            room_prefix=row["room_prefix"],
            sort_order=row["sort_order"],
        )


class SQLiteFloorRepository(FloorRepository):
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_by_project(self, project_id: int) -> list[Floor]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM floors WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        ).fetchall()
        return [self._row_to_floor(row) for row in rows]

    def list_by_building(self, project_id: int, building_id: int | None) -> list[Floor]:
        conn = self._connection.connect()
        if building_id is None:
            rows = conn.execute(
                """
                SELECT * FROM floors
                WHERE project_id = ? AND building_id IS NULL
                ORDER BY sort_order, id
                """,
                (project_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM floors
                WHERE project_id = ? AND building_id = ?
                ORDER BY sort_order, id
                """,
                (project_id, building_id),
            ).fetchall()
        return [self._row_to_floor(row) for row in rows]

    def get_by_id(self, floor_id: int) -> Optional[Floor]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM floors WHERE id = ?", (floor_id,)).fetchone()
        return self._row_to_floor(row) if row else None

    def save(self, floor: Floor) -> Floor:
        conn = self._connection.connect()
        if floor.id is None:
            cursor = conn.execute(
                "INSERT INTO floors (project_id, building_id, name, sort_order) VALUES (?, ?, ?, ?)",
                (floor.project_id, floor.building_id, floor.name, floor.sort_order),
            )
            floor.id = cursor.lastrowid
        else:
            conn.execute(
                "UPDATE floors SET name = ?, sort_order = ?, building_id = ? WHERE id = ?",
                (floor.name, floor.sort_order, floor.building_id, floor.id),
            )
        self._connection.commit()
        return floor

    def delete(self, floor_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("DELETE FROM floors WHERE id = ?", (floor_id,))
        self._connection.commit()

    def reorder(self, project_id: int, floor_ids: list[int]) -> None:
        conn = self._connection.connect()
        for index, floor_id in enumerate(floor_ids):
            conn.execute(
                "UPDATE floors SET sort_order = ? WHERE id = ? AND project_id = ?",
                (index, floor_id, project_id),
            )
        self._connection.commit()

    def _row_to_floor(self, row) -> Floor:
        building_id = row["building_id"] if "building_id" in row.keys() else None
        return Floor(
            id=row["id"],
            project_id=row["project_id"],
            building_id=building_id,
            name=row["name"],
            sort_order=row["sort_order"],
        )


class SQLiteRoomRepository(RoomRepository):
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_by_project(self, project_id: int) -> list[Room]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM rooms WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
        return [self._row_to_room(row) for row in rows]

    def get_by_id(self, room_id: int) -> Optional[Room]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        return self._row_to_room(row) if row else None

    def save(self, room: Room) -> Room:
        conn = self._connection.connect()
        if room.id is None:
            cursor = conn.execute(
                """
                INSERT INTO rooms (
                    project_id, floor_id, building_id, name, number, raw_area,
                    area_type, factor, calculation_path, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    room.project_id,
                    room.floor_id,
                    room.building_id,
                    room.name,
                    room.number,
                    room.raw_area,
                    room.area_type.value,
                    room.factor.decimal,
                    room.calculation_path,
                    room.note,
                ),
            )
            room.id = cursor.lastrowid
        else:
            conn.execute(
                """
                UPDATE rooms SET
                    floor_id = ?, building_id = ?, name = ?, number = ?, raw_area = ?,
                    area_type = ?, factor = ?, calculation_path = ?, note = ?
                WHERE id = ?
                """,
                (
                    room.floor_id,
                    room.building_id,
                    room.name,
                    room.number,
                    room.raw_area,
                    room.area_type.value,
                    room.factor.decimal,
                    room.calculation_path,
                    room.note,
                    room.id,
                ),
            )
        self._connection.commit()
        return room

    def save_many(self, rooms: list[Room]) -> list[Room]:
        return [self.save(room) for room in rooms]

    def delete(self, room_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        self._connection.commit()

    def restore(self, room: Room) -> Room:
        conn = self._connection.connect()
        if room.id is None:
            return self.save(room)
        conn.execute(
            """
            INSERT INTO rooms (
                id, project_id, floor_id, building_id, name, number, raw_area,
                area_type, factor, calculation_path, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                room.id,
                room.project_id,
                room.floor_id,
                room.building_id,
                room.name,
                room.number,
                room.raw_area,
                room.area_type.value,
                room.factor.decimal,
                room.calculation_path,
                room.note,
            ),
        )
        self._connection.commit()
        return room

    def _row_to_room(self, row) -> Room:
        area_type = AreaType(row["area_type"]) if row["area_type"] in {
            AreaType.WOHNFLAECHE.value,
            AreaType.NUTZFLAECHE.value,
        } else AreaType.NONE
        building_id = row["building_id"] if "building_id" in row.keys() else None
        return Room(
            id=row["id"],
            project_id=row["project_id"],
            floor_id=row["floor_id"],
            building_id=building_id,
            name=row["name"],
            number=row["number"],
            raw_area=row["raw_area"],
            area_type=area_type,
            factor=Factor.from_decimal(row["factor"]),
            calculation_path=row["calculation_path"],
            note=row["note"],
        )


class SQLiteTextBlockRepository(TextBlockRepository):
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_by_project(self, project_id: int) -> list[TextBlock]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM text_blocks WHERE project_id = ?",
            (project_id,),
        ).fetchall()
        return [self._row_to_text_block(row) for row in rows]

    def get_by_type(
        self, project_id: int, block_type: TextBlockType
    ) -> Optional[TextBlock]:
        conn = self._connection.connect()
        row = conn.execute(
            "SELECT * FROM text_blocks WHERE project_id = ? AND block_type = ?",
            (project_id, block_type.value),
        ).fetchone()
        return self._row_to_text_block(row) if row else None

    def save(self, text_block: TextBlock) -> TextBlock:
        conn = self._connection.connect()
        if text_block.id is None:
            cursor = conn.execute(
                "INSERT INTO text_blocks (project_id, block_type, content) VALUES (?, ?, ?)",
                (text_block.project_id, text_block.block_type.value, text_block.content),
            )
            text_block.id = cursor.lastrowid
        else:
            conn.execute(
                "UPDATE text_blocks SET content = ? WHERE id = ?",
                (text_block.content, text_block.id),
            )
        self._connection.commit()
        return text_block

    def _row_to_text_block(self, row) -> TextBlock:
        return TextBlock(
            id=row["id"],
            project_id=row["project_id"],
            block_type=TextBlockType(row["block_type"]),
            content=row["content"],
        )
