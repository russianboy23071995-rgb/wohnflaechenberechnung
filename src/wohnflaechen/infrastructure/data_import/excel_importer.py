"""Excel-Import für Archicad-Exporte."""

from pathlib import Path

import pandas as pd

from wohnflaechen.domain.entities.room import Room
from wohnflaechen.infrastructure.data_import.archicad_woflv_parser import (
    is_archicad_woflv_format,
    parse_archicad_woflv,
)
from wohnflaechen.infrastructure.data_import.import_models import ImportedRoom


COLUMN_ALIASES = {
    "name": ["raumname", "name", "room name", "room_name", "raum", "raumbeschreibung"],
    "number": ["raumnummer", "nummer", "number", "room number", "raumnr", "nr", "nr."],
    "area": [
        "fläche",
        "flaeche",
        "area",
        "fläche m²",
        "flaeche m2",
        "fläche [m²]",
        "flaeche [m2]",
        "m²",
        "m2",
    ],
    "floor": ["geschoss", "floor", "ebene", "level", "stockwerk"],
}


def _normalize_column_name(column: str) -> str:
    return str(column).strip().lower().replace("²", "2")


def _find_column(columns: list[str], aliases: list[str]) -> str | None:
    normalized = {_normalize_column_name(c): c for c in columns}
    for alias in aliases:
        key = _normalize_column_name(alias)
        if key in normalized:
            return normalized[key]
    return None


def _parse_area(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _is_empty_cell(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    return str(value).strip() in ("", "nan", "None")


class ExcelImporter:
    """Liest Archicad-Excel-Dateien und erzeugt Raumdaten."""

    def import_file(self, file_path: Path) -> list[ImportedRoom]:
        excel = pd.ExcelFile(file_path, engine="openpyxl")
        best: list[ImportedRoom] = []

        for sheet_name in excel.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl")
            if df.empty:
                continue
            rooms = self._import_dataframe(df)
            if len(rooms) > len(best):
                best = rooms

        return best

    def _import_dataframe(self, df: pd.DataFrame) -> list[ImportedRoom]:
        if is_archicad_woflv_format(df):
            return parse_archicad_woflv(df)
        return self._import_tabular(df)

    def _import_tabular(self, df: pd.DataFrame) -> list[ImportedRoom]:
        """Fallback für tabellarische Exporte mit Spaltenköpfen."""
        if df.shape[1] < 2:
            return []

        if is_archicad_woflv_format(df):
            return parse_archicad_woflv(df)

        header_row = None
        for row_idx in range(min(20, len(df))):
            row_values = [
                str(df.iloc[row_idx, col]).strip().lower()
                for col in range(df.shape[1])
                if not _is_empty_cell(df.iloc[row_idx, col])
            ]
            if any("raumbeschreibung" in v or "raumname" in v for v in row_values):
                header_row = row_idx
                break

        if header_row is not None:
            header_df = df.iloc[header_row:].copy()
            header_df.columns = header_df.iloc[0]
            data_df = header_df.iloc[1:].reset_index(drop=True)
        else:
            data_df = df
            data_df.columns = [f"col_{i}" for i in range(data_df.shape[1])]

        columns = list(data_df.columns)
        name_col = _find_column(columns, COLUMN_ALIASES["name"])
        number_col = _find_column(columns, COLUMN_ALIASES["number"])
        area_col = _find_column(columns, COLUMN_ALIASES["area"])
        floor_col = _find_column(columns, COLUMN_ALIASES["floor"])

        if not name_col and not number_col:
            raise ValueError(
                "Keine Raumspalten gefunden. Erwartet wird das Archicad-Rohformat "
                "(R-XXX in Spalte A) oder Spalten wie 'Raumbeschreibung' / 'Raumname'."
            )

        imported: list[ImportedRoom] = []
        for _, row in data_df.iterrows():
            name = str(row[name_col]).strip() if name_col else ""
            number = str(row[number_col]).strip() if number_col else ""
            if name in ("nan", "None"):
                name = ""
            if number in ("nan", "None"):
                number = ""

            if not name and not number:
                continue

            raw_area = _parse_area(row[area_col]) if area_col else 0.0
            floor_name = ""
            if floor_col and not _is_empty_cell(row[floor_col]):
                floor_name = str(row[floor_col]).strip()

            imported.append(
                ImportedRoom(
                    name=name,
                    number=number,
                    raw_area=raw_area,
                    floor_name=floor_name,
                )
            )

        return imported

    def to_rooms(
        self,
        imported_rooms: list[ImportedRoom],
        project_id: int,
        floor_map: dict[str, int],
    ) -> list[Room]:
        """Konvertiert Importdaten in Domain-Räume."""
        rooms: list[Room] = []
        for item in imported_rooms:
            floor_id = None
            if item.floor_name and item.floor_name in floor_map:
                floor_id = floor_map[item.floor_name]

            rooms.append(
                Room(
                    project_id=project_id,
                    floor_id=floor_id,
                    building_id=item.building_id,
                    name=item.name,
                    number=item.number,
                    raw_area=item.raw_area,
                    calculation_path=item.calculation_path,
                )
            )
        return rooms
