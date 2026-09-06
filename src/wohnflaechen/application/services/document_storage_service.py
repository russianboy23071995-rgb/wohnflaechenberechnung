"""Konfigurierbare Ablagepfade für Angebote, Rechnungen und WoFlV."""

import re
from pathlib import Path

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.invoice import Invoice
from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.infrastructure.database.auftrag_repositories import SQLiteAppSettingsRepository


def _sanitize_filename(text: str, max_len: int = 80) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]', "-", text.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned or "Dokument"


class DocumentStorageService:
    """Verwaltet den Wurzelpfad und erzeugt Zielpfade für Dokumente."""

    SUBDIR_OFFERS = "Angebote"
    SUBDIR_INVOICES = "Rechnungen"
    SUBDIR_WOFLV = "Wohnflaechenberechnung"

    def __init__(self, settings_repository: SQLiteAppSettingsRepository) -> None:
        self._settings = settings_repository

    def get_documents_root(self) -> Path | None:
        raw = self._settings.get(SQLiteAppSettingsRepository.KEY_DOCUMENTS_ROOT, "").strip()
        if not raw:
            return None
        path = Path(raw)
        return path if path.is_dir() else None

    def set_documents_root(self, path: Path) -> None:
        self._settings.set(
            SQLiteAppSettingsRepository.KEY_DOCUMENTS_ROOT,
            str(path.resolve()),
        )

    def ensure_subdir(self, subdir: str) -> Path:
        root = self.get_documents_root()
        if root is None:
            raise ValueError(
                "Kein Dokumentenablagepfad konfiguriert. "
                "Bitte unter Einstellungen → Dokumentenablage festlegen."
            )
        target = root / subdir
        target.mkdir(parents=True, exist_ok=True)
        return target

    def default_offer_path(self, auftrag: Auftrag, offer: Offer) -> Path:
        folder = self.ensure_subdir(self.SUBDIR_OFFERS)
        label = _sanitize_filename(offer.number or auftrag.display_title())
        obj = _sanitize_filename(auftrag.object_name or auftrag.title)
        filename = f"{label} - {obj} - Angebot.pdf"
        return folder / filename

    def default_invoice_path(self, auftrag: Auftrag, invoice: Invoice) -> Path:
        folder = self.ensure_subdir(self.SUBDIR_INVOICES)
        label = _sanitize_filename(invoice.number or auftrag.display_title())
        obj = _sanitize_filename(auftrag.object_name or auftrag.title)
        filename = f"{label} - {obj} - Rechnung.pdf"
        return folder / filename

    def default_woflv_path(self, auftrag: Auftrag | None, project: Project) -> Path:
        folder = self.ensure_subdir(self.SUBDIR_WOFLV)
        obj = _sanitize_filename(project.object_name or project.name or "WoFlV")
        if auftrag and auftrag.object_name:
            obj = _sanitize_filename(auftrag.object_name)
        filename = f"{obj} - WoFlV.pdf"
        return folder / filename
