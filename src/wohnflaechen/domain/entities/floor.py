"""Geschoss-Entität."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Floor:
    """Geschoss innerhalb eines Projekts."""

    id: Optional[int] = None
    project_id: int = 0
    building_id: Optional[int] = None
    name: str = ""
    sort_order: int = 0
