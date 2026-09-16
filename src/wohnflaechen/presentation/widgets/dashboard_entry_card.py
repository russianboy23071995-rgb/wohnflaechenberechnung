"""Kartenzeile für einen Auftrag / eine Berechnung – kompakt wenn abgeschlossen."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.dto.dashboard_entry import DashboardEntry


class _EntryCard(QFrame):
    open_hub = Signal(str)
    open_offer = Signal(str)
    open_woflv = Signal(str)
    open_invoice = Signal(str)
    toggle_completed = Signal(str)
    move_to_folder = Signal(str)

    def __init__(self, entry: DashboardEntry, parent=None) -> None:
        super().__init__(parent)
        self._entry = entry
        self._key = entry.key
        self._details_visible = not entry.completed
        self._apply_card_style()

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(8)
        self.expand_btn = QPushButton("▸")
        self.expand_btn.setObjectName("ghostButton")
        self.expand_btn.setFixedSize(28, 28)
        self.expand_btn.clicked.connect(self._toggle_details)
        if not entry.completed:
            self.expand_btn.hide()

        self.title_label = QLabel(entry.title)
        self.title_label.setObjectName("entryTitle")
        self.date_label = QLabel(entry.date_label())
        self.date_label.setObjectName("entryMeta")

        status = QLabel("Abgeschlossen" if entry.completed else "Aktiv")
        status.setObjectName("statusBadgeDone" if entry.completed else "statusBadgePending")

        header.addWidget(self.expand_btn)
        header.addWidget(self.title_label, stretch=1)
        header.addWidget(status)
        header.addWidget(self.date_label)
        root.addLayout(header)

        self.meta_label = QLabel(
            f"{entry.client or '—'}"
            + (f" · {entry.object_address}" if entry.object_address else "")
        )
        self.meta_label.setObjectName("entryMeta")
        self.meta_label.setWordWrap(True)
        root.addWidget(self.meta_label)

        self.details = QWidget()
        details_layout = QVBoxLayout(self.details)
        details_layout.setContentsMargins(0, 4, 0, 0)
        details_layout.setSpacing(8)

        badges = QHBoxLayout()
        badges.setSpacing(8)
        badges.addWidget(self._badge("Angebot", entry.has_offer, entry.offer_number))
        badges.addWidget(self._badge("WoFlV", entry.has_woflv, ""))
        badges.addWidget(self._badge("Rechnung", entry.has_invoice, entry.invoice_number))
        badges.addStretch()
        details_layout.addLayout(badges)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        hub_btn = QPushButton("Projektpanel")
        hub_btn.setObjectName("primaryButton")
        hub_btn.setMinimumHeight(36)
        hub_btn.clicked.connect(lambda: self.open_hub.emit(self._key))
        actions.addWidget(hub_btn)

        if entry.auftrag_id is not None:
            offer_btn = QPushButton("Angebot")
            offer_btn.setObjectName("ghostButton")
            offer_btn.clicked.connect(lambda: self.open_offer.emit(self._key))
            actions.addWidget(offer_btn)

            invoice_btn = QPushButton("Rechnung")
            invoice_btn.setObjectName("ghostButton")
            invoice_btn.clicked.connect(lambda: self.open_invoice.emit(self._key))
            actions.addWidget(invoice_btn)

        woflv_btn = QPushButton("WoFlV öffnen")
        woflv_btn.setObjectName("secondaryButton")
        woflv_btn.setEnabled(entry.has_woflv or entry.project_id is not None)
        if not entry.has_woflv and entry.auftrag_id is not None:
            woflv_btn.setText("WoFlV starten")
            woflv_btn.setEnabled(True)
        woflv_btn.clicked.connect(lambda: self.open_woflv.emit(self._key))
        actions.addWidget(woflv_btn)

        complete_label = "Wieder öffnen" if entry.completed else "Als abgeschlossen markieren"
        complete_btn = QPushButton(complete_label)
        complete_btn.setObjectName("ghostButton")
        complete_btn.clicked.connect(lambda: self.toggle_completed.emit(self._key))
        actions.addWidget(complete_btn)

        folder_btn = QPushButton("In Ordner …")
        folder_btn.setObjectName("ghostButton")
        folder_btn.clicked.connect(lambda: self.move_to_folder.emit(self._key))
        actions.addWidget(folder_btn)

        actions.addStretch()
        details_layout.addLayout(actions)
        root.addWidget(self.details)

        self._sync_details_visibility()

    def _apply_card_style(self) -> None:
        self.setObjectName("entryCardCompact" if self._entry.completed else "entryCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)

    def _toggle_details(self) -> None:
        self._details_visible = not self._details_visible
        self._sync_details_visibility()

    def _sync_details_visibility(self) -> None:
        if self._entry.completed:
            self.expand_btn.setText("▾" if self._details_visible else "▸")
            self.details.setVisible(self._details_visible)
            self.meta_label.setVisible(self._details_visible)
        else:
            self.details.setVisible(True)
            self.meta_label.setVisible(True)

    def _badge(self, label: str, done: bool, detail: str) -> QLabel:
        if done and detail:
            text = f"{label}: {detail}"
        elif done:
            text = f"✓ {label}"
        else:
            text = f"○ {label}"
        badge = QLabel(text)
        badge.setObjectName("statusBadgeDone" if done else "statusBadgePending")
        return badge
