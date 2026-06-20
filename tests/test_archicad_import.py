"""Tests für Archicad WoFlV Excel-Import."""

from pathlib import Path

import pandas as pd

from wohnflaechen.infrastructure.data_import.archicad_woflv_parser import (
    is_archicad_woflv_format,
    parse_archicad_woflv,
)
from wohnflaechen.infrastructure.data_import.excel_importer import ExcelImporter

SAMPLE_PATH = Path(
    r"c:\Users\cnovi\iCloudDrive\NOVIKOV PLAN & Maß\Aufträge\2026\Mai"
    r"\Böhmskamp 28 - 23569 Lübeck\Wohnflächenberechnung_Roh.xlsx"
)


def test_archicad_sample_file():
    if not SAMPLE_PATH.is_file():
        return

    df = pd.read_excel(SAMPLE_PATH, header=None, engine="openpyxl")
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
    imported = importer.import_file(SAMPLE_PATH)
    assert len(imported) == 19


if __name__ == "__main__":
    test_archicad_sample_file()
    print("OK")
