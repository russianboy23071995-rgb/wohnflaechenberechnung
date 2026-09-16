"""Projekt-Entität."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Project:
    """Stammdaten eines Wohnflächenberechnungs-Projekts."""

    id: Optional[int] = None
    auftrag_id: Optional[int] = None
    name: str = ""
    object_name: str = ""
    address: str = ""
    client: str = ""
    editor: str = ""
    measurement_date: Optional[date] = None
    measurement_on_site: bool = True
    measurement_note: str = ""
    created_at: Optional[datetime] = None
    notes: str = ""
    file_path: str = ""
    completed: bool = False

    def display_title(self) -> str:
        if self.object_name:
            return self.object_name
        return self.name or "Unbenanntes Projekt"
