"""Permanente Zusammenfassung – rechte Seitenleiste."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.services.calculation_service import CalculationService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.enums.area_type import AreaType


class SummaryWidget(QWidget):
    """Zeigt Gesamtsummen und Geschoss-Aufschlüsselung zur Fehlerkontrolle."""

    export_pdf_requested = Signal()

    def __init__(
        self,
        room_service: RoomService,
        floor_service: FloorService,
        calculation_service: CalculationService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._room_service = room_service
        self._floor_service = floor_service
        self._calculation_service = calculation_service
        self._project_id: int | None = None
        self._live_rooms: list[Room] | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Zusammenfassung")
        title.setStyleSheet("font-weight: 700; font-size: 11pt;")
        layout.addWidget(title)

        hint = QLabel(
            "Kontrollübersicht vor dem PDF-Export. "
            "Anrechnungsfaktoren dienen nur der Deklaration."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint)

        self.total_living_label = QLabel("Gesamtwohnfläche: 0,00 m²")
        self.total_usable_label = QLabel("Gesamtnutzfläche: 0,00 m²")
        self.total_living_label.setStyleSheet("font-weight: 700;")
        self.total_usable_label.setStyleSheet("font-weight: 700;")
        layout.addWidget(self.total_living_label)
        layout.addWidget(self.total_usable_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Geschoss", "Nutzfläche", "Wohnfläche"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, stretch=1)

        self.unassigned_label = QLabel("")
        self.unassigned_label.setWordWrap(True)
        self.unassigned_label.setStyleSheet("color: #a44; font-size: 9pt;")
        layout.addWidget(self.unassigned_label)

        self.export_pdf_button = QPushButton("PDF exportieren")
        self.export_pdf_button.setMinimumHeight(40)
        self.export_pdf_button.setStyleSheet(
            "font-weight: 600; font-size: 10pt; padding: 8px 12px;"
        )
        self.export_pdf_button.clicked.connect(self.export_pdf_requested.emit)
        layout.addWidget(self.export_pdf_button, alignment=Qt.AlignmentFlag.AlignRight)

    def set_export_enabled(self, enabled: bool) -> None:
        self.export_pdf_button.setEnabled(enabled)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self._live_rooms = None
        self.set_export_enabled(project_id is not None)
        self.refresh()

    def refresh(self, rooms: list[Room] | None = None) -> None:
        self._live_rooms = rooms
        if self._project_id is None:
            self._clear()
            return

        if rooms is None:
            rooms = self._room_service.list_rooms(self._project_id)
        floors = self._floor_service.list_floors(self._project_id)
        summary = self._calculation_service.summarize(rooms, floors)

        self.total_living_label.setText(
            f"Gesamtwohnfläche: {self._format_area(summary.total_living_area)}"
        )
        self.total_usable_label.setText(
            f"Gesamtnutzfläche: {self._format_area(summary.total_usable_area)}"
        )

        self.table.setRowCount(0)
        for floor_summary in summary.floor_summaries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self._set_cell(row, 0, floor_summary.floor_name)
            self._set_cell(row, 1, self._format_optional(floor_summary.usable_area))
            self._set_cell(row, 2, self._format_optional(floor_summary.living_area))

        unassigned = [room for room in rooms if room.floor_id is None]
        undeclared = [
            room for room in rooms
            if room.area_type == AreaType.NONE and room.floor_id is not None
        ]
        hints: list[str] = []
        if unassigned:
            hints.append(f"{len(unassigned)} Raum/Räume ohne Geschoss")
        if undeclared:
            hints.append(f"{len(undeclared)} zugeordnete Räume ohne Flächenart")
        self.unassigned_label.setText(" · ".join(hints))

    def _clear(self) -> None:
        self.total_living_label.setText("Gesamtwohnfläche: 0,00 m²")
        self.total_usable_label.setText("Gesamtnutzfläche: 0,00 m²")
        self.table.setRowCount(0)
        self.unassigned_label.setText("")

    def _set_cell(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        if col == 0:
            align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        else:
            align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        item.setTextAlignment(align)
        self.table.setItem(row, col, item)

    def _format_area(self, value: float) -> str:
        return f"{value:.2f} m²".replace(".", ",")

    def _format_optional(self, value: float) -> str:
        if value == 0:
            return ""
        return self._format_area(value)
