"""Gebäude-Entität – z. B. Haus 1 (R-) und Haus 2 (E-)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Building:
    """Gebäude innerhalb eines Projekts (mehrere Häuser pro Bauantrag)."""

    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    room_prefix: str = ""
    sort_order: int = 0
