"""Startbildschirm mit Firmenbranding."""

from pathlib import Path

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
    DOCUMENT_TITLE_LINE_1,
    DOCUMENT_TITLE_LINE_2,
    DOCUMENT_SUBTITLE,
)

_LOGO_PATH = Path(__file__).parent.parent / "pdf" / "static" / "logo_icon.png"


class WelcomeWidget(QWidget):
    """Willkommensansicht vor Projektstart."""

    create_project = Signal()
    open_project = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        if _LOGO_PATH.is_file():
            logo = QLabel()
            pixmap = QPixmap(str(_LOGO_PATH))
            scaled = pixmap.scaledToHeight(96, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(scaled)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo)

        company = QLabel(COMPANY_NAME)
        company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(company)

        tagline = QLabel(COMPANY_TAGLINE)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-size: 11pt; color: #555;")
        layout.addWidget(tagline)

        subtitle = QLabel(
            f"{DOCUMENT_TITLE_LINE_1} · {DOCUMENT_TITLE_LINE_2} · {DOCUMENT_SUBTITLE}"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 13pt; margin-top: 8px;")
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        create_btn = QPushButton("Wohnflächenberechnung erstellen")
        create_btn.setMinimumWidth(280)
        create_btn.setMinimumHeight(42)
        create_btn.setStyleSheet(
            "font-size: 11pt; font-weight: 600; padding: 8px 16px;"
        )
        create_btn.clicked.connect(self.create_project.emit)
        layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        open_btn = QPushButton("Bestehendes Projekt öffnen")
        open_btn.setMinimumWidth(280)
        open_btn.clicked.connect(self.open_project.emit)
        layout.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(
            "Neues Projekt: Geschosse festlegen, Excel-Rohdatei importieren, "
            "Objektdaten erfassen – danach Räume zuordnen und Flächen deklarieren."
        )
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #666; max-width: 520px; margin-top: 16px;")
        layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignCenter)
