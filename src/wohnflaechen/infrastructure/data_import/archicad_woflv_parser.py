"""Archicad WoFlV-Excel-Format (Wohnflächenberechnung_Roh.xlsx und Varianten)."""

import re
from dataclasses import dataclass

import pandas as pd

from wohnflaechen.infrastructure.data_import.import_models import ImportedRoom
from wohnflaechen.infrastructure.data_import.room_prefix import (
    detect_room_prefix,
    is_archicad_room_label,
)

# Spalten (0-basiert): A=Bezeichnung, B=Name/Rechenweg, C=Flächenvorschau, F=Ergebnisse
COL_LABEL = 0
COL_TEXT = 1
COL_AREA_PREVIEW = 2
COL_RESULT = 5

NUMERIC_ROOM_PATTERN = re.compile(r"^\d{1,4}$")
CALC_LINE_PATTERN = re.compile(r"^\d+:$")
END_MARKERS = ("Summe Wohnfläche", "Summe Nutzfläche", "Wohnungen in dem")


@dataclass
class _RoomBlock:
    number: str
    name: str
    raw_area: float
    calculation_lines: list[str]


def _cell_value(df: pd.DataFrame, row: int, col: int) -> object:
    if row >= len(df) or col >= df.shape[1]:
        return None
    return df.iloc[row, col]


def _cell_str(df: pd.DataFrame, row: int, col: int) -> str:
    value = _cell_value(df, row, col)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if text in ("nan", "None"):
        return ""
    return text


def is_room_label(label: str) -> bool:
    """Raumkennung: Archicad R-/E-XXX oder numerische Nr."""
    return is_archicad_room_label(label)


def _parse_german_float(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "")
    if not text:
        return 0.0
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _trim_german_number(value: str) -> str:
    value = value.strip()
    if "," not in value:
        return value
    whole, frac = value.split(",", 1)
    frac = frac.rstrip("0")
    if not frac:
        return whole
    return f"{whole},{frac}"


def _format_formula(formula: str) -> str:
    """Wandelt Archicad-Formeln in lesbaren Berechnungsweg."""
    text = formula.strip()
    if not text:
        return ""

    div_suffix = ""
    if "/" in text:
        base, divisor = text.rsplit("/", 1)
        divisor = divisor.strip()
        if re.fullmatch(r"\d+", divisor):
            text = base.strip()
            div_suffix = f" / {divisor}"

    parts = [p.strip() for p in text.split("*") if p.strip()]
    if not parts:
        return formula

    formatted = " x ".join(f"{_trim_german_number(part)} m" for part in parts)
    return formatted + div_suffix


def _is_end_marker(label: str) -> bool:
    return any(marker in label for marker in END_MARKERS)


def _is_woflv_header_row(df: pd.DataFrame, row: int) -> bool:
    header_nr = _cell_str(df, row, COL_LABEL).lower().replace(".", "")
    header_name = _cell_str(df, row, COL_TEXT).lower()
    return header_nr in ("nr", "nr.") and "raumbeschreibung" in header_name


def _find_woflv_data_start(df: pd.DataFrame) -> int | None:
    """Findet die erste Datenzeile nach Kopf „Nr. / Raumbeschreibung“."""
    for row in range(min(40, len(df))):
        if not _is_woflv_header_row(df, row):
            continue
        for candidate in (row + 2, row + 1):
            if candidate >= len(df):
                continue
            label = _cell_str(df, candidate, COL_LABEL)
            name = _cell_str(df, candidate, COL_TEXT)
            if is_room_label(label) and name:
                return candidate
    return None


def _parse_room_block(df: pd.DataFrame, start_row: int) -> tuple[_RoomBlock, int]:
    number = _cell_str(df, start_row, COL_LABEL)
    name = _cell_str(df, start_row, COL_TEXT)
    raw_area = _parse_german_float(_cell_value(df, start_row, COL_AREA_PREVIEW))

    calculation_lines: list[str] = []
    row = start_row + 1
    in_deduction = False

    while row < len(df):
        label = _cell_str(df, row, COL_LABEL)

        if is_room_label(label):
            break
        if label and _is_end_marker(label):
            break

        if label == "Fläche":
            in_deduction = False
            row += 1
            continue

        if label.lower() == "schraffurabzug":
            calculation_lines.append("Abzüge und Dachschrägen:")
            in_deduction = True
            row += 1
            continue

        if label.startswith("Summe"):
            row += 1
            continue

        if label.startswith("Rundungskorrektur"):
            row += 1
            continue

        if CALC_LINE_PATTERN.match(label):
            formula = _cell_str(df, row, COL_TEXT)
            if formula:
                line = _format_formula(formula)
                if in_deduction:
                    line = f"- {line}"
                elif calculation_lines and not calculation_lines[-1].startswith("Abzüge"):
                    line = f"+ {line}"
                calculation_lines.append(line)
            row += 1
            continue

        row += 1

    block = _RoomBlock(
        number=number,
        name=name,
        raw_area=round(raw_area, 2),
        calculation_lines=calculation_lines,
    )
    return block, row


def is_archicad_woflv_format(df: pd.DataFrame) -> bool:
    """Erkennt WoFlV-Rohdaten (R-/E-XXX oder numerische Nr. mit Raumbeschreibung)."""
    data_start = _find_woflv_data_start(df)
    if data_start is not None:
        return True

    scan_from = data_start if data_start is not None else 0
    for row in range(scan_from, min(len(df), scan_from + 300)):
        label = _cell_str(df, row, COL_LABEL)
        if detect_room_prefix(label):
            return True
        if NUMERIC_ROOM_PATTERN.match(label) and _cell_str(df, row, COL_TEXT):
            return True
    return False


def parse_archicad_woflv(df: pd.DataFrame) -> list[ImportedRoom]:
    """Parst Archicad-Wohnflächen-Rohdaten (alle bekannten Varianten)."""
    imported: list[ImportedRoom] = []
    row = _find_woflv_data_start(df)
    if row is None:
        row = 0

    while row < len(df):
        label = _cell_str(df, row, COL_LABEL)
        if not is_room_label(label):
            row += 1
            continue

        name = _cell_str(df, row, COL_TEXT)
        if not name:
            row += 1
            continue

        block, next_row = _parse_room_block(df, row)
        imported.append(
            ImportedRoom(
                name=block.name,
                number=block.number,
                raw_area=block.raw_area,
                floor_name="",
                calculation_path="\n".join(block.calculation_lines),
            )
        )
        row = next_row

    return imported
