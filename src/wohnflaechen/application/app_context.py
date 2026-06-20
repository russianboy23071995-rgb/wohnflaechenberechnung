"""Zentraler Service-Container für die Application-Schicht."""

from pathlib import Path

from wohnflaechen.application.services.calculation_service import CalculationService
from wohnflaechen.application.services.document_export_service import DocumentExportService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.import_service import ImportService
from wohnflaechen.application.services.project_service import ProjectService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.infrastructure.database.connection import DatabaseConnection
from wohnflaechen.infrastructure.database.repositories import (
    SQLiteFloorRepository,
    SQLiteProjectRepository,
    SQLiteRoomRepository,
    SQLiteTextBlockRepository,
)
from wohnflaechen.infrastructure.data_import.excel_importer import ExcelImporter


def get_default_db_path() -> Path:
    base = Path.home() / ".novikov_wohnflaechen"
    return base / "projects.db"


class AppContext:
    """Verdrahtet Repositories und Services."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_default_db_path()
        self.connection = DatabaseConnection(self.db_path)

        self.project_repository = SQLiteProjectRepository(self.connection)
        self.floor_repository = SQLiteFloorRepository(self.connection)
        self.room_repository = SQLiteRoomRepository(self.connection)
        self.text_block_repository = SQLiteTextBlockRepository(self.connection)

        self.project_service = ProjectService(
            self.connection,
            self.project_repository,
            self.text_block_repository,
        )
        self.floor_service = FloorService(self.floor_repository)
        self.room_service = RoomService(self.room_repository)
        self.text_block_service = TextBlockService(self.text_block_repository)
        self.import_service = ImportService(
            self.room_service,
            self.floor_service,
            ExcelImporter(),
        )
        self.calculation_service = CalculationService()
        self.document_export_service = DocumentExportService(
            self.project_service,
            self.floor_service,
            self.room_service,
            self.text_block_service,
            self.calculation_service,
        )
        self._pdf_engine = None

        self.project_service.initialize_database()

    @property
    def pdf_engine(self):
        if self._pdf_engine is None:
            from wohnflaechen.presentation.pdf.engine import PdfEngine

            self._pdf_engine = PdfEngine()
        return self._pdf_engine
