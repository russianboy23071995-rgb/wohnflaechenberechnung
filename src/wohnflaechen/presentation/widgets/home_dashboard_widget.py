"""Zentrales Start-Dashboard – Übersicht und Schnellzugriff."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.dto.dashboard_entry import DashboardEntry
from wohnflaechen.application.services.client_profile_service import ClientProfileService
from wohnflaechen.presentation.pdf.branding import COMPANY_NAME, COMPANY_TAGLINE
from wohnflaechen.presentation.widgets.auftrag_inline_panel import AuftragInlinePanel
from wohnflaechen.presentation.widgets.dashboard_entry_card import _EntryCard


class HomeDashboardWidget(QWidget):
    """Startseite mit Schnellaktionen und Projektliste."""

    auftrag_submitted = Signal(object, str)
    woflv_only_requested = Signal()
    settings_requested = Signal()

    open_hub = Signal(str)
    open_offer = Signal(str)
    open_woflv = Signal(str)
    open_invoice = Signal(str)
    toggle_completed = Signal(str)
    move_to_folder = Signal(str)

    def __init__(
        self,
        client_profile_service: ClientProfileService | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appBackground")
        self._profile_service = client_profile_service
        self._entries: list[DashboardEntry] = []
        self._entry_map: dict[str, DashboardEntry] = {}
        self._nav_category: str | None = None
        self._nav_folder_id: int | None = None
        self._folder_item_keys: set[str] = set()
        self._build_ui()

    def _build_ui(self) -> None:
        main_column = QVBoxLayout(self)
        main_column.setContentsMargins(16, 0, 8, 0)
        main_column.setSpacing(20)

        hero = QWidget()
        hero.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero_layout.setSpacing(6)

        brand = QLabel(COMPANY_NAME)
        brand.setObjectName("brandTitle")
        hero_layout.addWidget(brand)

        tagline = QLabel(COMPANY_TAGLINE)
        tagline.setObjectName("brandSubtitle")
        hero_layout.addWidget(tagline)

        headline = QLabel("Ihr Arbeitsplatz für Angebote, WoFlV und Rechnungen")
        headline.setObjectName("heroHeadline")
        hero_layout.addWidget(headline)

        sub = QLabel(
            "Starten Sie einen neuen Vorgang oder springen Sie direkt "
            "in Angebot, Berechnung oder Rechnung – alles von hier."
        )
        sub.setObjectName("hintText")
        sub.setWordWrap(True)
        hero_layout.addWidget(sub)
        main_column.addWidget(hero)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        btn_full = QPushButton("Neuer Auftrag")
        btn_full.setObjectName("primaryButton")
        btn_full.setMinimumHeight(40)
        btn_full.clicked.connect(self._on_neuer_auftrag_clicked)
        actions_row.addWidget(btn_full)

        btn_offer = QPushButton("Nur Angebot")
        btn_offer.setObjectName("secondaryButton")
        btn_offer.setMinimumHeight(40)
        btn_offer.clicked.connect(lambda: self._expand_auftrag_panel("offer"))
        actions_row.addWidget(btn_offer)

        btn_woflv = QPushButton("Nur WoFlV")
        btn_woflv.setObjectName("secondaryButton")
        btn_woflv.setMinimumHeight(40)
        btn_woflv.clicked.connect(self.woflv_only_requested.emit)
        actions_row.addWidget(btn_woflv)

        btn_invoice = QPushButton("Nur Rechnung")
        btn_invoice.setObjectName("secondaryButton")
        btn_invoice.setMinimumHeight(40)
        btn_invoice.clicked.connect(lambda: self._expand_auftrag_panel("invoice"))
        actions_row.addWidget(btn_invoice)

        btn_settings = QPushButton("Einstellungen")
        btn_settings.setObjectName("ghostButton")
        btn_settings.setMinimumHeight(40)
        btn_settings.clicked.connect(self.settings_requested.emit)
        actions_row.addWidget(btn_settings)
        actions_row.addStretch()
        main_column.addLayout(actions_row)

        self.auftrag_panel = AuftragInlinePanel()
        self.auftrag_panel.submitted.connect(self._on_auftrag_panel_submitted)
        self.auftrag_panel.profile_picker_requested.connect(self.profile_picker_requested.emit)
        main_column.addWidget(self.auftrag_panel)

        list_header = QHBoxLayout()
        self.list_title = QLabel("Ihre Vorgänge")
        self.list_title.setObjectName("sectionTitle")
        list_header.addWidget(self.list_title)
        list_header.addStretch()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Suchen …")
        self.search_edit.setMinimumWidth(180)
        self.search_edit.textChanged.connect(self._apply_filter)
        list_header.addWidget(self.search_edit)
        main_column.addLayout(list_header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("dashboardScroll")
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()

        self.empty_label = QLabel("Noch keine Vorgänge – starten Sie oben mit einem neuen Auftrag.")
        self.empty_label.setObjectName("hintText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)

        self.scroll.setWidget(self.list_container)
        main_column.addWidget(self.scroll, stretch=1)

    profile_picker_requested = Signal()

    def set_folder_filter(
        self,
        category: str | None,
        folder_id: int | None,
        folder_item_keys: set[str],
        list_title: str,
    ) -> None:
        self._nav_category = category
        self._nav_folder_id = folder_id
        self._folder_item_keys = folder_item_keys
        self.list_title.setText(list_title)
        self._apply_filter(self.search_edit.text())

    def show_new_auftrag_panel(self) -> None:
        self.auftrag_panel.toggle_new()

    def expand_auftrag_panel(self, follow_up: str = "") -> None:
        self.auftrag_panel.expand_new(follow_up)

    def collapse_auftrag_panel(self) -> None:
        self.auftrag_panel.collapse()

    def collapse_all_panels(self) -> None:
        self.collapse_auftrag_panel()

    def apply_client_profile(self, profile) -> None:
        self.auftrag_panel.apply_client_profile(profile)

    def _on_neuer_auftrag_clicked(self) -> None:
        self.show_new_auftrag_panel()

    def _expand_auftrag_panel(self, follow_up: str) -> None:
        self.expand_auftrag_panel(follow_up)

    def _on_auftrag_panel_submitted(self, auftrag, follow_up: str) -> None:
        self.auftrag_submitted.emit(auftrag, follow_up)

    def set_entries(self, entries: list[DashboardEntry]) -> None:
        self._entries = entries
        self._entry_map = {e.key: e for e in entries}
        self._apply_filter(self.search_edit.text())

    def _matches_nav_filter(self, entry: DashboardEntry) -> bool:
        if self._nav_folder_id is None:
            return True
        if self._folder_item_keys:
            return entry.key in self._folder_item_keys
        category = self._nav_category or ""
        if category == "angebote":
            return entry.has_offer
        if category == "rechnungen":
            return entry.has_invoice
        if category == "kunden":
            return bool(entry.client.strip())
        if category == "objekte":
            return bool(entry.object_address.strip() or entry.title.strip())
        return True

    def _apply_filter(self, text: str = "") -> None:
        needle = text.strip().lower()
        filtered = [e for e in self._entries if self._matches_nav_filter(e)]
        if needle:
            filtered = [
                e
                for e in filtered
                if needle in e.title.lower()
                or needle in e.client.lower()
                or needle in e.object_address.lower()
            ]

        active = [e for e in filtered if not e.completed]
        done = [e for e in filtered if e.completed]

        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget and widget is not self.empty_label:
                widget.deleteLater()

        if not filtered:
            self.empty_label.setVisible(True)
            if self.empty_label.parent() is None:
                self.list_layout.insertWidget(0, self.empty_label)
            if needle:
                self.empty_label.setText("Keine Treffer für die Suche.")
            else:
                self.empty_label.setText(
                    "Noch keine Vorgänge – starten Sie oben mit einem neuen Auftrag."
                )
            return

        self.empty_label.setVisible(False)
        if self.empty_label.parent() is not None:
            self.list_layout.removeWidget(self.empty_label)
            self.empty_label.hide()

        insert_at = 0
        for entry in active:
            card = _EntryCard(entry)
            card.open_hub.connect(self.open_hub.emit)
            card.open_offer.connect(self.open_offer.emit)
            card.open_woflv.connect(self.open_woflv.emit)
            card.open_invoice.connect(self.open_invoice.emit)
            card.toggle_completed.connect(self.toggle_completed.emit)
            card.move_to_folder.connect(self.move_to_folder.emit)
            self.list_layout.insertWidget(insert_at, card)
            insert_at += 1

        if done:
            sep = QLabel("Abgeschlossen")
            sep.setObjectName("hintText")
            self.list_layout.insertWidget(insert_at, sep)
            insert_at += 1
            for entry in done:
                card = _EntryCard(entry)
                card.open_hub.connect(self.open_hub.emit)
                card.open_offer.connect(self.open_offer.emit)
                card.open_woflv.connect(self.open_woflv.emit)
                card.open_invoice.connect(self.open_invoice.emit)
                card.toggle_completed.connect(self.toggle_completed.emit)
                card.move_to_folder.connect(self.move_to_folder.emit)
                self.list_layout.insertWidget(insert_at, card)
                insert_at += 1
