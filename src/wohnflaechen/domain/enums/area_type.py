"""Flächenarten für Räume."""

from enum import Enum


class AreaType(str, Enum):
    """Zuordnung eines Raums zu Wohn- oder Nutzfläche."""

    NONE = ""
    WOHNFLAECHE = "Wohnfläche"
    NUTZFLAECHE = "Nutzfläche"

    @classmethod
    def choices(cls) -> list[str]:
        return [cls.WOHNFLAECHE.value, cls.NUTZFLAECHE.value]
