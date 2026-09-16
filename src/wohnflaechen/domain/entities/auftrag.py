"""Auftrag – übergeordneter Vorgang (Angebot → WoFlV → Rechnung)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Auftrag:
    """Stammdaten eines Auftrags mit Kunde und Objekt."""

    id: Optional[int] = None
    title: str = ""
    client_name: str = ""
    client_address: str = ""
    client_email: str = ""
    client_phone: str = ""
    object_name: str = ""
    object_address: str = ""
    editor: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    completed: bool = False

    def display_title(self) -> str:
        if self.object_name:
            return self.object_name
        if self.title:
            return self.title
        if self.client_name:
            return self.client_name
        return "Unbenannter Auftrag"
