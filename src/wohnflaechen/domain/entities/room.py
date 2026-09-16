"""Raum-Entität."""

from dataclasses import dataclass
from typing import Optional

from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor


@dataclass
class Room:
    """Raum im zentralen Raum-Pool."""

    id: Optional[int] = None
    project_id: int = 0
    floor_id: Optional[int] = None
    building_id: Optional[int] = None
    name: str = ""
    number: str = ""
    raw_area: float = 0.0
    area_type: AreaType = AreaType.NONE
    factor: Factor = Factor.FULL
    calculation_path: str = ""
    note: str = ""

    @property
    def credited_area(self) -> float:
        """Anrechenbare Fläche (bereits im Berechnungsweg enthalten).

        Der Anrechnungsfaktor dient nur der Deklaration im PDF, nicht der
        erneuten Multiplikation.
        """
        return round(self.raw_area, 2)

    @property
    def living_area(self) -> float:
        if self.area_type == AreaType.WOHNFLAECHE:
            return self.credited_area
        return 0.0

    @property
    def usable_area(self) -> float:
        if self.area_type == AreaType.NUTZFLAECHE:
            return self.credited_area
        return 0.0
