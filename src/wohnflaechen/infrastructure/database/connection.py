"""SQLite-Verbindungsverwaltung."""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """Verwaltet eine SQLite-Verbindung pro Projektdatei."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def path(self) -> Path:
        return self._db_path

    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def commit(self) -> None:
        if self._connection is not None:
            self._connection.commit()
