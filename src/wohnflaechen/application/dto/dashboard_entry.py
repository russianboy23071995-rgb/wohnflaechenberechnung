"""Eintrag auf dem Start-Dashboard."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DashboardEntry:
    """Ein Auftrag oder eine eigenständige WoFlV-Berechnung."""

    key: str
    title: str
    client: str
    object_address: str
    created_at: Optional[datetime]
    auftrag_id: Optional[int] = None
    project_id: Optional[int] = None
    has_offer: bool = False
    has_woflv: bool = False
    has_invoice: bool = False
    offer_number: str = ""
    invoice_number: str = ""
    completed: bool = False

    @property
    def is_standalone_woflv(self) -> bool:
        return self.auftrag_id is None and self.project_id is not None

    def date_label(self) -> str:
        if not self.created_at:
            return ""
        return self.created_at.strftime("%d.%m.%Y")
