"""Auftraggeber-Profil für wiederkehrende Kunden."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClientProfile:
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    email: str = ""
    phone: str = ""
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def display_label(self) -> str:
        if self.name:
            return self.name
        return "Unbenannt"

    def subtitle(self) -> str:
        parts = [p for p in (self.address, self.email) if p]
        return " · ".join(parts) if parts else ""
