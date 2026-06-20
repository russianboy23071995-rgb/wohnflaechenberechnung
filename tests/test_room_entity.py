"""Tests für Raum-Entität."""

from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor


def test_credited_area_ignores_factor():
    room = Room(raw_area=10.0, factor=Factor.QUARTER, area_type=AreaType.WOHNFLAECHE)
    assert room.credited_area == 10.0
    assert room.living_area == 10.0


def test_factor_quarter_does_not_reduce_usable_area():
    room = Room(raw_area=6.59, factor=Factor.QUARTER, area_type=AreaType.NUTZFLAECHE)
    assert room.usable_area == 6.59
