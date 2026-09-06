"""Startbildschirm mit Firmenbranding."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.presentation.pdf.branding import (
    COMPANY_NAME,
    COMPANY_TAGLINE,
)
from wohnflaechen.presentation.paths import pdf_static_file


class WelcomeWidget(QWidget):
    """Willkommensansicht – Auftrag oder bestehende Berechnung."""

    create_auftrag = Signal()
    open_auftrag = Signal()
    standalone_woflv = Signal()
    open_standalone_project = Signal()
    settings_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appBackground")
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(24, 24, 24, 24)

        card = QWidget()
        card.setObjectName("welcomeCard")
        card.setMaximumWidth(580)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 36, 40, 36)

        logo_path = pdf_static_file("logo_icon.png")
        if logo_path.is_file():
            logo = QLabel()
            pixmap = QPixmap(str(logo_path))
            scaled = pixmap.scaledToHeight(88, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(scaled)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo)

        company = QLabel(COMPANY_NAME)
        company.setObjectName("brandTitle")
        company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company)

        tagline = QLabel(COMPANY_TAGLINE)
        tagline.setObjectName("brandSubtitle")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        layout.addSpacing(12)

        auftrag_btn = QPushButton("Neuer Auftrag (Angebot → WoFlV → Rechnung)")
        auftrag_btn.setObjectName("primaryButton")
        auftrag_btn.setMinimumWidth(320)
        auftrag_btn.setMinimumHeight(44)
        auftrag_btn.clicked.connect(self.create_auftrag.emit)
        layout.addWidget(auftrag_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        open_auftrag_btn = QPushButton("Auftrag öffnen")
        open_auftrag_btn.setMinimumWidth(320)
        open_auftrag_btn.setMinimumHeight(38)
        open_auftrag_btn.clicked.connect(self.open_auftrag.emit)
        layout.addWidget(open_auftrag_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(8)

        standalone_btn = QPushButton("Nur Wohnflächenberechnung (ohne Auftrag)")
        standalone_btn.setMinimumWidth(320)
        standalone_btn.setMinimumHeight(38)
        standalone_btn.clicked.connect(self.standalone_woflv.emit)
        layout.addWidget(standalone_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        open_proj_btn = QPushButton("Bestehende Berechnung öffnen")
        open_proj_btn.setMinimumWidth(320)
        open_proj_btn.setMinimumHeight(38)
        open_proj_btn.clicked.connect(self.open_standalone_project.emit)
        layout.addWidget(open_proj_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        settings_btn = QPushButton("Einstellungen …")
        settings_btn.setMinimumWidth(320)
        settings_btn.clicked.connect(self.settings_requested.emit)
        layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(
            "Empfohlener Ablauf: Auftrag anlegen → Angebot → Wohnflächenberechnung → Rechnung. "
            "Dokumente werden im konfigurierten Ablageordner gespeichert."
        )
        hint.setObjectName("hintText")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addWidget(card)
