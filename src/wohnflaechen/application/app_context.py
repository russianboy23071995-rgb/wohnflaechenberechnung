"""Zentraler Service-Container für die Application-Schicht."""

from pathlib import Path

from wohnflaechen.application.services.auftrag_service import AuftragService
from wohnflaechen.application.services.calculation_service import CalculationService
from wohnflaechen.application.services.document_export_service import DocumentExportService
from wohnflaechen.application.services.document_storage_service import DocumentStorageService
from wohnflaechen.application.services.building_service import BuildingService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.folder_service import FolderService
from wohnflaechen.application.services.room_undo_service import RoomUndoService
from wohnflaechen.application.services.import_service import ImportService
from wohnflaechen.application.services.invoice_service import InvoiceService
from wohnflaechen.application.services.offer_service import OfferService
from wohnflaechen.application.services.project_service import ProjectService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.application.services.text_block_service import TextBlockService
from wohnflaechen.application.services.client_profile_service import ClientProfileService
from wohnflaechen.application.services.layout_settings_service import LayoutSettingsService
from wohnflaechen.infrastructure.database.client_profile_repository import SQLiteClientProfileRepository
from wohnflaechen.infrastructure.database.auftrag_repositories import (
    SQLiteAppSettingsRepository,
    SQLiteAuftragRepository,
    SQLiteInvoiceRepository,
    SQLiteOfferRepository,
)
from wohnflaechen.infrastructure.database.folder_repository import SQLiteFolderRepository
from wohnflaechen.infrastructure.database.connection import DatabaseConnection
from wohnflaechen.infrastructure.database.repositories import (
    SQLiteBuildingRepository,
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
        self.building_repository = SQLiteBuildingRepository(self.connection)
        self.room_repository = SQLiteRoomRepository(self.connection)
        self.text_block_repository = SQLiteTextBlockRepository(self.connection)
        self.auftrag_repository = SQLiteAuftragRepository(self.connection)
        self.offer_repository = SQLiteOfferRepository(self.connection)
        self.invoice_repository = SQLiteInvoiceRepository(self.connection)
        self.settings_repository = SQLiteAppSettingsRepository(self.connection)
        self.client_profile_repository = SQLiteClientProfileRepository(self.connection)
        self.folder_repository = SQLiteFolderRepository(self.connection)

        self.project_service = ProjectService(
            self.connection,
            self.project_repository,
            self.text_block_repository,
        )
        self.floor_service = FloorService(self.floor_repository)
        self.building_service = BuildingService(self.building_repository)
        self.room_service = RoomService(self.room_repository, self.floor_repository)
        self.text_block_service = TextBlockService(self.text_block_repository)
        self.import_service = ImportService(
            self.room_service,
            self.floor_service,
            self.building_service,
            ExcelImporter(),
        )
        self.calculation_service = CalculationService()
        self.document_export_service = DocumentExportService(
            self.project_service,
            self.floor_service,
            self.building_service,
            self.room_service,
            self.text_block_service,
            self.calculation_service,
        )
        self.document_storage_service = DocumentStorageService(self.settings_repository)
        self.auftrag_service = AuftragService(self.auftrag_repository, self.project_repository)
        self.client_profile_service = ClientProfileService(self.client_profile_repository)
        self.folder_service = FolderService(self.folder_repository)
        self.layout_settings_service = LayoutSettingsService(self.settings_repository)
        self.room_undo_service = RoomUndoService(self.room_repository)
        self.offer_service = OfferService(self.offer_repository)
        self.invoice_service = InvoiceService(self.invoice_repository)

        self._pdf_engine = None
        self._commercial_pdf_engine = None

        self.project_service.initialize_database()

    @property
    def pdf_engine(self):
        if self._pdf_engine is None:
            from wohnflaechen.presentation.pdf.engine import PdfEngine

            self._pdf_engine = PdfEngine()
        return self._pdf_engine

    @property
    def commercial_pdf_engine(self):
        if self._commercial_pdf_engine is None:
            from wohnflaechen.presentation.pdf.commercial_engine import CommercialPdfEngine

            self._commercial_pdf_engine = CommercialPdfEngine()
        return self._commercial_pdf_engine
