"""SQLite-Repositories für Aufträge, Angebote und Rechnungen."""

from datetime import date, datetime
from typing import Optional

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.invoice import Invoice
from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.infrastructure.database.connection import DatabaseConnection


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


class SQLiteAuftragRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def list_all(self) -> list[Auftrag]:
        conn = self._connection.connect()
        rows = conn.execute("SELECT * FROM auftraege ORDER BY created_at DESC").fetchall()
        return [self._row_to_auftrag(row) for row in rows]

    def get_by_id(self, auftrag_id: int) -> Optional[Auftrag]:
        conn = self._connection.connect()
        row = conn.execute("SELECT * FROM auftraege WHERE id = ?", (auftrag_id,)).fetchone()
        return self._row_to_auftrag(row) if row else None

    def save(self, auftrag: Auftrag) -> Auftrag:
        conn = self._connection.connect()
        created_at = auftrag.created_at or datetime.now()
        if auftrag.id is None:
            cursor = conn.execute(
                """
                INSERT INTO auftraege (
                    title, client_name, client_address, client_email, client_phone,
                    object_name, object_address, editor, notes, created_at, completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    auftrag.title,
                    auftrag.client_name,
                    auftrag.client_address,
                    auftrag.client_email,
                    auftrag.client_phone,
                    auftrag.object_name,
                    auftrag.object_address,
                    auftrag.editor,
                    auftrag.notes,
                    created_at.isoformat(),
                    1 if auftrag.completed else 0,
                ),
            )
            auftrag.id = cursor.lastrowid
            auftrag.created_at = created_at
        else:
            conn.execute(
                """
                UPDATE auftraege SET
                    title = ?, client_name = ?, client_address = ?, client_email = ?,
                    client_phone = ?, object_name = ?, object_address = ?, editor = ?,
                    notes = ?, completed = ?
                WHERE id = ?
                """,
                (
                    auftrag.title,
                    auftrag.client_name,
                    auftrag.client_address,
                    auftrag.client_email,
                    auftrag.client_phone,
                    auftrag.object_name,
                    auftrag.object_address,
                    auftrag.editor,
                    auftrag.notes,
                    1 if auftrag.completed else 0,
                    auftrag.id,
                ),
            )
        self._connection.commit()
        return auftrag

    def delete(self, auftrag_id: int) -> None:
        conn = self._connection.connect()
        conn.execute("DELETE FROM auftraege WHERE id = ?", (auftrag_id,))
        self._connection.commit()

    def _row_to_auftrag(self, row) -> Auftrag:
        return Auftrag(
            id=row["id"],
            title=row["title"],
            client_name=row["client_name"],
            client_address=row["client_address"],
            client_email=row["client_email"],
            client_phone=row["client_phone"],
            object_name=row["object_name"],
            object_address=row["object_address"],
            editor=row["editor"],
            notes=row["notes"],
            created_at=_parse_datetime(row["created_at"]),
            completed=bool(row["completed"]) if "completed" in row.keys() else False,
        )


class SQLiteOfferRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def get_by_auftrag(self, auftrag_id: int) -> Optional[Offer]:
        conn = self._connection.connect()
        row = conn.execute(
            "SELECT * FROM angebote WHERE auftrag_id = ? ORDER BY created_at DESC LIMIT 1",
            (auftrag_id,),
        ).fetchone()
        return self._row_to_offer(row) if row else None

    def list_by_auftrag(self, auftrag_id: int) -> list[Offer]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM angebote WHERE auftrag_id = ? ORDER BY created_at DESC",
            (auftrag_id,),
        ).fetchall()
        return [self._row_to_offer(row) for row in rows]

    def save(self, offer: Offer) -> Offer:
        conn = self._connection.connect()
        created_at = offer.created_at or datetime.now()
        offer_date = offer.date.isoformat() if offer.date else None
        if offer.id is None:
            cursor = conn.execute(
                """
                INSERT INTO angebote (
                    auftrag_id, number, date, service_description, price,
                    notes, file_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer.auftrag_id,
                    offer.number,
                    offer_date,
                    offer.service_description,
                    offer.price,
                    offer.notes,
                    offer.file_path,
                    created_at.isoformat(),
                ),
            )
            offer.id = cursor.lastrowid
            offer.created_at = created_at
        else:
            conn.execute(
                """
                UPDATE angebote SET
                    number = ?, date = ?, service_description = ?, price = ?,
                    notes = ?, file_path = ?
                WHERE id = ?
                """,
                (
                    offer.number,
                    offer_date,
                    offer.service_description,
                    offer.price,
                    offer.notes,
                    offer.file_path,
                    offer.id,
                ),
            )
        self._connection.commit()
        return offer

    def count_all(self) -> int:
        conn = self._connection.connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM angebote").fetchone()
        return int(row["c"])

    def _row_to_offer(self, row) -> Offer:
        return Offer(
            id=row["id"],
            auftrag_id=row["auftrag_id"],
            number=row["number"],
            date=_parse_date(row["date"]),
            service_description=row["service_description"],
            price=float(row["price"]),
            notes=row["notes"],
            file_path=row["file_path"],
            created_at=_parse_datetime(row["created_at"]),
        )


class SQLiteInvoiceRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def get_by_auftrag(self, auftrag_id: int) -> Optional[Invoice]:
        conn = self._connection.connect()
        row = conn.execute(
            "SELECT * FROM rechnungen WHERE auftrag_id = ? ORDER BY created_at DESC LIMIT 1",
            (auftrag_id,),
        ).fetchone()
        return self._row_to_invoice(row) if row else None

    def list_by_auftrag(self, auftrag_id: int) -> list[Invoice]:
        conn = self._connection.connect()
        rows = conn.execute(
            "SELECT * FROM rechnungen WHERE auftrag_id = ? ORDER BY created_at DESC",
            (auftrag_id,),
        ).fetchall()
        return [self._row_to_invoice(row) for row in rows]

    def save(self, invoice: Invoice) -> Invoice:
        conn = self._connection.connect()
        created_at = invoice.created_at or datetime.now()
        invoice_date = invoice.date.isoformat() if invoice.date else None
        if invoice.id is None:
            cursor = conn.execute(
                """
                INSERT INTO rechnungen (
                    auftrag_id, number, date, service_description, price,
                    notes, file_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice.auftrag_id,
                    invoice.number,
                    invoice_date,
                    invoice.service_description,
                    invoice.price,
                    invoice.notes,
                    invoice.file_path,
                    created_at.isoformat(),
                ),
            )
            invoice.id = cursor.lastrowid
            invoice.created_at = created_at
        else:
            conn.execute(
                """
                UPDATE rechnungen SET
                    number = ?, date = ?, service_description = ?, price = ?,
                    notes = ?, file_path = ?
                WHERE id = ?
                """,
                (
                    invoice.number,
                    invoice_date,
                    invoice.service_description,
                    invoice.price,
                    invoice.notes,
                    invoice.file_path,
                    invoice.id,
                ),
            )
        self._connection.commit()
        return invoice

    def count_all(self) -> int:
        conn = self._connection.connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM rechnungen").fetchone()
        return int(row["c"])

    def _row_to_invoice(self, row) -> Invoice:
        return Invoice(
            id=row["id"],
            auftrag_id=row["auftrag_id"],
            number=row["number"],
            date=_parse_date(row["date"]),
            service_description=row["service_description"],
            price=float(row["price"]),
            notes=row["notes"],
            file_path=row["file_path"],
            created_at=_parse_datetime(row["created_at"]),
        )


class SQLiteAppSettingsRepository:
    KEY_DOCUMENTS_ROOT = "documents_root_path"

    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def get(self, key: str, default: str = "") -> str:
        conn = self._connection.connect()
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        conn = self._connection.connect()
        conn.execute(
            """
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        self._connection.commit()
