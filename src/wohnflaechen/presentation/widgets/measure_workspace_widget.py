"""Arbeitsbereich „Maßen ermitteln“ – PDF-Artboard."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.presentation.measure.measure_canvas_view import MeasureCanvasView


class MeasureWorkspaceWidget(QWidget):
    back_requested = Signal()
    continue_to_woflv_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("appBackground")
        self._auftrag: Auftrag | None = None
        self._pending_pdf: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.title_label = QLabel("Maßen ermitteln")
        self.title_label.setObjectName("headerTitle")
        header.addWidget(self.title_label)
        header.addStretch()

        self.back_btn = QPushButton("← Auftragpanel")
        self.back_btn.setObjectName("ghostButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)
        layout.addLayout(header)

        hint = QLabel(
            "PDF-Grundrisse auf das Artboard legen, verschieben und an den Ecken skalieren. "
            "Mausrad = Scrollen, Strg+Mausrad = Zoom, Mittelklick = Schwenken."
        )
        hint.setObjectName("hintText")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.add_pdf_btn = QPushButton("PDF hinzufügen …")
        self.add_pdf_btn.setObjectName("primaryButton")
        self.add_pdf_btn.clicked.connect(self._add_pdf)
        toolbar.addWidget(self.add_pdf_btn)

        toolbar.addWidget(QLabel("Seite:"))
        self.page_combo = QComboBox()
        self.page_combo.setMinimumWidth(72)
        self.page_combo.setEnabled(False)
        toolbar.addWidget(self.page_combo)

        self.insert_page_btn = QPushButton("Seite einfügen")
        self.insert_page_btn.setObjectName("secondaryButton")
        self.insert_page_btn.setEnabled(False)
        self.insert_page_btn.clicked.connect(self._insert_selected_page)
        toolbar.addWidget(self.insert_page_btn)

        self.zoom_fit_btn = QPushButton("Alles einpassen")
        self.zoom_fit_btn.setObjectName("secondaryButton")
        self.zoom_fit_btn.clicked.connect(self._zoom_fit)
        toolbar.addWidget(self.zoom_fit_btn)

        self.clear_btn = QPushButton("Leeren")
        self.clear_btn.setObjectName("ghostButton")
        self.clear_btn.clicked.connect(self._clear_canvas)
        toolbar.addWidget(self.clear_btn)

        toolbar.addStretch()
        self.status_label = QLabel("Keine PDFs")
        self.status_label.setObjectName("hintText")
        toolbar.addWidget(self.status_label)
        layout.addLayout(toolbar)

        self.canvas = MeasureCanvasView()
        self.canvas.setObjectName("glassPanel")
        self.canvas.items_changed.connect(self._update_status)
        layout.addWidget(self.canvas, stretch=1)

    def set_auftrag(self, auftrag: Auftrag | None) -> None:
        self._auftrag = auftrag
        if auftrag:
            self.title_label.setText(f"Maßen ermitteln – {auftrag.display_title()}")
        else:
            self.title_label.setText("Maßen ermitteln")

    def _add_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF-Grundriss wählen",
            "",
            "PDF-Dateien (*.pdf)",
        )
        if not path:
            return
        file_path = Path(path)
        page_count = self.canvas.page_count(file_path)
        if page_count <= 0:
            QMessageBox.warning(
                self,
                "PDF",
                "Die Datei konnte nicht gelesen werden oder enthält keine Seiten.",
            )
            return

        if page_count == 1:
            item = self.canvas.add_pdf(file_path, 0)
            if item is None:
                QMessageBox.warning(self, "PDF", "Seite konnte nicht geladen werden.")
            return

        self._pending_pdf = file_path
        self.page_combo.clear()
        for index in range(page_count):
            self.page_combo.addItem(str(index + 1), index)
        self.page_combo.setEnabled(True)
        self.insert_page_btn.setEnabled(True)
        self.page_combo.setCurrentIndex(0)
        self._insert_selected_page()

    def _insert_selected_page(self) -> None:
        if self._pending_pdf is None:
            return
        page_index = self.page_combo.currentData()
        if page_index is None:
            page_index = self.page_combo.currentIndex()
        item = self.canvas.add_pdf(self._pending_pdf, int(page_index))
        if item is None:
            QMessageBox.warning(self, "PDF", "Seite konnte nicht geladen werden.")

    def _zoom_fit(self) -> None:
        self.canvas.zoom_fit()

    def _clear_canvas(self) -> None:
        if not self.canvas.pdf_items():
            return
        confirm = QMessageBox.question(
            self,
            "Artboard leeren",
            "Alle PDFs vom Artboard entfernen?",
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.canvas.clear_all()
            self._pending_pdf = None
            self.page_combo.clear()
            self.page_combo.setEnabled(False)
            self.insert_page_btn.setEnabled(False)

    def _update_status(self) -> None:
        count = len(self.canvas.pdf_items())
        if count == 0:
            self.status_label.setText("Keine PDFs")
        elif count == 1:
            self.status_label.setText("1 PDF auf dem Artboard")
        else:
            self.status_label.setText(f"{count} PDFs auf dem Artboard")
