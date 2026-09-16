"""SQLite-Repository für Auftraggeber-Profile."""

from datetime import datetime
from typing import Optional

from wohnflaechen.domain.entities.client_profile import ClientProfile
from wohnflaechen.infrastructure.database.connection import DatabaseConnection


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


class SQLiteClientProfileRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_all(self) -> list[ClientProfile]:
        conn = self._connection.connect()
        rows = conn.execute(
            """
            SELECT * FROM client_profiles
            ORDER BY last_used_at DESC, name COLLATE NOCASE ASC
            """
        ).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def get_by_id(self, profile_id: int) -> Optional[ClientProfile]:
        conn = self._connection.connect()
        row = conn.execute(
            "SELECT * FROM client_profiles WHERE id = ?",
            (profile_id,),
        ).fetchone()
        return self._row_to_profile(row) if row else None

    def find_by_name(self, name: str) -> Optional[ClientProfile]:
        normalized = name.strip().lower()
        if not normalized:
            return None
        conn = self._connection.connect()
        row = conn.execute(
            """
            SELECT * FROM client_profiles
            WHERE lower(trim(name)) = ?
            LIMIT 1
            """,
            (normalized,),
        ).fetchone()
        return self._row_to_profile(row) if row else None

    def save(self, profile: ClientProfile) -> ClientProfile:
        conn = self._connection.connect()
        now = datetime.now()
        last_used = profile.last_used_at or now
        created_at = profile.created_at or now
        if profile.id is None:
            cursor = conn.execute(
                """
                INSERT INTO client_profiles (
                    name, address, email, phone, last_used_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.name.strip(),
                    profile.address.strip(),
                    profile.email.strip(),
                    profile.phone.strip(),
                    last_used.isoformat(),
                    created_at.isoformat(),
                ),
            )
            profile.id = cursor.lastrowid
            profile.created_at = created_at
            profile.last_used_at = last_used
        else:
            conn.execute(
                """
                UPDATE client_profiles SET
                    name = ?, address = ?, email = ?, phone = ?,
                    last_used_at = ?
                WHERE id = ?
                """,
                (
                    profile.name.strip(),
                    profile.address.strip(),
                    profile.email.strip(),
                    profile.phone.strip(),
                    last_used.isoformat(),
                    profile.id,
                ),
            )
            profile.last_used_at = last_used
        self._connection.commit()
        return profile

    def upsert_from_fields(
        self,
        name: str,
        address: str,
        email: str,
        phone: str,
    ) -> Optional[ClientProfile]:
        name = name.strip()
        if not name:
            return None
        existing = self.find_by_name(name)
        profile = existing or ClientProfile(name=name)
        profile.name = name
        profile.address = address.strip()
        profile.email = email.strip()
        profile.phone = phone.strip()
        profile.last_used_at = datetime.now()
        return self.save(profile)

    def _row_to_profile(self, row) -> ClientProfile:
        return ClientProfile(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            email=row["email"],
            phone=row["phone"],
            last_used_at=_parse_datetime(row["last_used_at"]),
            created_at=_parse_datetime(row["created_at"]),
        )
