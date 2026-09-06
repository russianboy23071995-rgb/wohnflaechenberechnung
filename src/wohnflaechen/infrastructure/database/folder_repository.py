"""SQLite-Repository für Ordnerstruktur."""

from typing import Optional

from wohnflaechen.domain.entities.folder import Folder
from wohnflaechen.infrastructure.database.connection import DatabaseConnection


class SQLiteFolderRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_all(self) -> list[Folder]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM folders ORDER BY sort_order, name COLLATE NOCASE"
        ).fetchall()
        return [self._row_to_folder(row) for row in rows]

    def get_by_id(self, folder_id: int) -> Optional[Folder]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM folders WHERE id = ?", (folder_id,)).fetchone()
        return self._row_to_folder(row) if row else None

    def save(self, folder: Folder) -> Folder:
        conn = self._connection.connect()
        if folder.id is None:
            cursor = conn.execute(
                """
                INSERT INTO folders (name, parent_id, category, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (folder.name, folder.parent_id, folder.category, folder.sort_order),
            )
            folder.id = cursor.lastrowid
        else:
            conn.execute(
                """
                UPDATE folders SET name = ?, parent_id = ?, category = ?, sort_order = ?
                WHERE id = ?
                """,
                (folder.name, folder.parent_id, folder.category, folder.sort_order, folder.id),
            )
        self._connection.commit()
        return folder

    def delete(self, folder_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        self._connection.commit()

    def list_items(self, folder_id: int) -> list[tuple[str, int]]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT entity_type, entity_id FROM folder_items WHERE folder_id = ?",
            (folder_id,),
        ).fetchall()
        return [(row["entity_type"], row["entity_id"]) for row in rows]

    def move_item(self, folder_id: int, entity_type: str, entity_id: int) -> None:
        conn = self._connection.connect()
        conn.execute(
            "DELETE FROM folder_items WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id),
        )
        conn.execute(
            """
            INSERT INTO folder_items (folder_id, entity_type, entity_id)
            VALUES (?, ?, ?)
            """,
            (folder_id, entity_type, entity_id),
        )
        self._connection.commit()

    def items_for_entity(self, entity_type: str, entity_id: int) -> list[int]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT folder_id FROM folder_items WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id),
        ).fetchall()
        return [row["folder_id"] for row in rows]

    def _row_to_folder(self, row) -> Folder:
        return Folder(
            id=row["id"],
            name=row["name"],
            parent_id=row["parent_id"],
            category=row["category"],
            sort_order=row["sort_order"],
        )
