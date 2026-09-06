"""Tests für Archicad WoFlV Excel-Import."""

from pathlib import Path

import pandas as pd

from wohnflaechen.infrastructure.data_import.archicad_woflv_parser import (
    is_archicad_woflv_format,
    is_room_label,
    parse_archicad_woflv,
)
from wohnflaechen.infrastructure.data_import.excel_importer import ExcelImporter

BOHMSKAMP_PATH = Path(
    r"c:\Users\cnovi\iCloudDrive\NOVIKOV PLAN & Maß\Aufträge\2026\Mai"
    r"\Böhmskamp 28 - 23569 Lübeck\Wohnflächenberechnung_Roh.xlsx"
)
HECKSCHER_PATH = Path(
    r"c:\Users\cnovi\iCloudDrive\MINIJOB\Heckscherstraße 33 WHG 1\WoFIV Roh.xlsx"
)


def _make_numeric_woflv_df() -> pd.DataFrame:
    """Minimales WoFlV-Layout mit numerischen Raumnummern."""
    rows = [
        ["5. Berechnung (basierend auf einem CAD-Modell)", None, None],
        ["Nr.", "Raumbeschreibung", "Fläche [m²]"],
        [None, None, "Zu berechnende Fläche [m²]"],
        ["01", "Zimmer 1", "12,3540"],
        ["Fläche", None, None],
        ["1:", "2,9000 * 4,2600", None],
        ["Summe:", None, None],
        ["Rundungskorrektur:", None, None],
        ["02", "Zimmer 2", "9,1228"],
        ["Fläche", None, None],
        ["1:", "2,4500 * 3,3486", None],
        ["2:", "2,4500 * 0,7500 / 2", None],
        ["Summe:", None, None],
        ["Rundungskorrektur:", None, None],
    ]
    return pd.DataFrame(rows)


def test_is_room_label_variants():
    assert is_room_label("R-002")
    assert is_room_label("r-099")
    assert is_room_label("01")
    assert is_room_label("08")
    assert not is_room_label("1:")
    assert not is_room_label("Fläche")
    assert not is_room_label("Summe:")


def test_numeric_woflv_fixture():
    df = _make_numeric_woflv_df()
    assert is_archicad_woflv_format(df)
    rooms = parse_archicad_woflv(df)
    assert len(rooms) == 2
    assert rooms[0].number == "01"
    assert rooms[0].name == "Zimmer 1"
    assert rooms[0].raw_area == 12.35
    assert "2,9 m x 4,26 m" in rooms[0].calculation_path
    assert rooms[1].number == "02"
    assert "+ 2,45 m x 0,75 m / 2" in rooms[1].calculation_path


def test_numeric_woflv_via_importer():
    df = _make_numeric_woflv_df()
    importer = ExcelImporter()
    rooms = importer._import_dataframe(df)
    assert len(rooms) == 2


def test_archicad_bohmskamp_sample_file():
    if not BOHMSKAMP_PATH.is_file():
        return

    df = pd.read_excel(BOHMSKAMP_PATH, header=None, engine="openpyxl")
    assert is_archicad_woflv_format(df)

    rooms = parse_archicad_woflv(df)
    assert len(rooms) == 19
    assert rooms[0].number == "R-002"
    assert rooms[0].name == "Heizraum"
    assert rooms[0].raw_area == 6.59
    assert "1,74 m x 3,38 m" in rooms[0].calculation_path

    schlafen = next(r for r in rooms if r.name == "Schlafen")
    assert "Abzüge und Dachschrägen:" in schlafen.calculation_path
    assert "- 3,4499 m x 0,59 m" in schlafen.calculation_path or "- 3,45 m x 0,59 m" in schlafen.calculation_path

    importer = ExcelImporter()
    imported = importer.import_file(BOHMSKAMP_PATH)
    assert len(imported) == 19


def test_heckscher_numeric_sample_file():
    if not HECKSCHER_PATH.is_file():
        return

    df = pd.read_excel(HECKSCHER_PATH, header=None, engine="openpyxl")
    assert is_archicad_woflv_format(df)

    rooms = parse_archicad_woflv(df)
    assert len(rooms) == 8
    assert rooms[0].number == "01"
    assert rooms[0].name == "Zimmer 1"
    assert rooms[0].raw_area == 12.35

    kueche = next(r for r in rooms if r.number == "06")
    assert kueche.name.lower().startswith("k")
    assert kueche.raw_area == 19.5
    assert len(kueche.calculation_path.split("\n")) >= 8

    importer = ExcelImporter()
    imported = importer.import_file(HECKSCHER_PATH)
    assert len(imported) == 8
