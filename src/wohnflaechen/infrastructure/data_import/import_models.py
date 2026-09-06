"""Datenmodell für Excel-Import."""

from dataclasses import dataclass


@dataclass
class ImportedRoom:
    """Zwischenergebnis eines Excel-Imports."""

    name: str
    number: str
    raw_area: float
    floor_name: str
    calculation_path: str = ""
    building_id: int | None = None
