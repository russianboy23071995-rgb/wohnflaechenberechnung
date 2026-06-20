"""Anrechnungsfaktoren für Flächenberechnungen."""

from enum import Enum


class Factor(str, Enum):
    """Standard-Anrechnungsfaktoren in Prozent."""

    ZERO = "0 %"
    QUARTER = "25 %"
    HALF = "50 %"
    FULL = "100 %"

    @property
    def decimal(self) -> float:
        mapping = {
            Factor.ZERO: 0.0,
            Factor.QUARTER: 0.25,
            Factor.HALF: 0.5,
            Factor.FULL: 1.0,
        }
        return mapping[self]

    @classmethod
    def from_decimal(cls, value: float) -> "Factor":
        mapping = {0.0: cls.ZERO, 0.25: cls.QUARTER, 0.5: cls.HALF, 1.0: cls.FULL}
        if value in mapping:
            return mapping[value]
        return cls.FULL

    @classmethod
    def choices(cls) -> list[str]:
        return [f.value for f in cls]
