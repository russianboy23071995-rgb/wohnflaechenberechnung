"""Ordner in der Navigationsstruktur."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Folder:
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None
    category: str = "vorgaenge"
    sort_order: int = 0

    def is_root(self) -> bool:
        return self.parent_id is None
