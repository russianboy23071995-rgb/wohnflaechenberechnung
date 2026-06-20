"""Excel-Import Use Cases."""

from pathlib import Path

from wohnflaechen.application.dto.import_result import ImportResult
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.infrastructure.data_import.excel_importer import ExcelImporter


class ImportService:
    """Importiert Archicad-Excel-Dateien in den Raum-Pool."""

    def __init__(
        self,
        room_service: RoomService,
        floor_service: FloorService,
        excel_importer: ExcelImporter,
    ) -> None:
        self._rooms = room_service
        self._floors = floor_service
        self._importer = excel_importer

    def import_excel(self, project_id: int, file_path: Path) -> ImportResult:
        imported = self._importer.import_file(file_path)
        result = ImportResult()

        if not imported:
            result.warnings.append("Die Excel-Datei enthält keine importierbaren Räume.")
            return result

        floor_map = self._floors.floor_map_by_name(project_id)
        new_floor_names: set[str] = set()

        for item in imported:
            if item.floor_name and item.floor_name not in floor_map:
                new_floor = self._floors.create_floor(project_id, item.floor_name)
                floor_map[item.floor_name] = new_floor.id
                new_floor_names.add(item.floor_name)

        rooms = self._importer.to_rooms(imported, project_id, floor_map)
        saved = self._rooms.save_rooms(rooms)

        result.imported_count = len(saved)
        result.new_floors = sorted(new_floor_names)
        return result
