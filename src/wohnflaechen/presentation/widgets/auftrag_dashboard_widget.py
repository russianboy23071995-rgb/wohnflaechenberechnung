"""Auftrags-Hub – Schritte Angebot, WoFlV, Rechnung."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.invoice import Invoice
from wohnflaechen.domain.entities.offer import Offer
from wohnflaechen.domain.entities.project import Project


class AuftragDashboardWidget(QWidget):
    edit_auftrag_requested = Signal()
    offer_requested = Signal()
    woflv_requested = Signal()
    woflv_open_requested = Signal()
    measure_requested = Signal()
    invoice_requested = Signal()
    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("appBackground")
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 24, 32, 24)
        outer.setSpacing(16)

        hub = QWidget()
        hub.setObjectName("hubCard")
        layout = QVBoxLayout(hub)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.panel_heading = QLabel("Projektpanel")
        self.panel_heading.setObjectName("heroHeadline")
        layout.addWidget(self.panel_heading)

        self.title_label = QLabel()
        self.title_label.setObjectName("hintText")
        layout.addWidget(self.title_label)

        self.meta_label = QLabel()
        self.meta_label.setObjectName("hintText")
        self.meta_label.setWordWrap(True)
        layout.addWidget(self.meta_label)

        self.step1_status = QLabel()
        self.step2_status = QLabel()
        self.step3_status = QLabel()
        for lbl in (self.step1_status, self.step2_status, self.step3_status):
            lbl.setWordWrap(True)
            lbl.setObjectName("entryMeta")
            layout.addWidget(lbl)

        row1 = QHBoxLayout()
        self.offer_btn = QPushButton("1 · Angebot")
        self.offer_btn.setObjectName("secondaryButton")
        self.offer_btn.setMinimumHeight(40)
        self.offer_btn.clicked.connect(self.offer_requested.emit)
        row1.addWidget(self.offer_btn)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.woflv_btn = QPushButton("2 · WoFlV starten")
        self.woflv_btn.setObjectName("secondaryButton")
        self.woflv_btn.setMinimumHeight(40)
        self.woflv_btn.clicked.connect(self.woflv_requested.emit)
        self.woflv_open_btn = QPushButton("WoFlV öffnen")
        self.woflv_open_btn.setObjectName("primaryButton")
        self.woflv_open_btn.setMinimumHeight(40)
        self.woflv_open_btn.clicked.connect(self.woflv_open_requested.emit)
        row2.addWidget(self.woflv_btn)
        row2.addWidget(self.woflv_open_btn)
        layout.addLayout(row2)

        row_measure = QHBoxLayout()
        self.measure_btn = QPushButton("Maßen ermitteln")
        self.measure_btn.setObjectName("primaryButton")
        self.measure_btn.setMinimumHeight(40)
        self.measure_btn.clicked.connect(self.measure_requested.emit)
        row_measure.addWidget(self.measure_btn)
        layout.addLayout(row_measure)

        row3 = QHBoxLayout()
        self.invoice_btn = QPushButton("3 · Rechnung")
        self.invoice_btn.setObjectName("secondaryButton")
        self.invoice_btn.setMinimumHeight(40)
        self.invoice_btn.clicked.connect(self.invoice_requested.emit)
        row3.addWidget(self.invoice_btn)
        layout.addLayout(row3)

        bottom = QHBoxLayout()
        self.edit_btn = QPushButton("Stammdaten")
        self.edit_btn.setObjectName("ghostButton")
        self.edit_btn.clicked.connect(self.edit_auftrag_requested.emit)
        self.back_btn = QPushButton("← Dashboard")
        self.back_btn.setObjectName("ghostButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        bottom.addWidget(self.edit_btn)
        bottom.addStretch()
        bottom.addWidget(self.back_btn)
        layout.addLayout(bottom)

        outer.addWidget(hub)
        outer.addStretch()

    def refresh(
        self,
        auftrag: Auftrag,
        offer: Offer | None,
        project: Project | None,
        invoice: Invoice | None,
    ) -> None:
        name = auftrag.display_title()
        self.panel_heading.setText(f"Projektpanel – {name}")
        self.title_label.setText(
            f"Auftraggeber: {auftrag.client_name or '—'} · "
            f"Objekt: {auftrag.object_name or '—'}"
        )
        self.meta_label.setText(
            f"Auftraggeber: {auftrag.client_name or '—'}\n"
            f"Objekt: {auftrag.object_name or '—'}\n"
            f"Adresse: {auftrag.object_address or '—'}"
        )

        if offer:
            self.step1_status.setText(
                f"✓ Angebot {offer.number} – "
                f"{offer.price:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        else:
            self.step1_status.setText("○ Angebot noch nicht erstellt")

        if project:
            aufmass = "Ja" if project.measurement_on_site else "Nein (Bestandsunterlagen)"
            self.step2_status.setText(f"✓ WoFlV vorhanden – Aufmaß: {aufmass}")
        else:
            self.step2_status.setText("○ WoFlV noch nicht gestartet")

        if invoice:
            self.step3_status.setText(
                f"✓ Rechnung {invoice.number} – "
                f"{invoice.price:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        else:
            self.step3_status.setText("○ Rechnung noch nicht erstellt")

        self.woflv_open_btn.setEnabled(project is not None)
