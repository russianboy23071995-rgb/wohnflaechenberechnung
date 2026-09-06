"""Raum-Pool – zentrale Arbeitsoberfläche mit Mehrfachauswahl und Drag-and-Drop."""

from collections.abc import Callable

from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QColor, QDrag
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.application.services.room_service import RoomService
from wohnflaechen.domain.entities.floor import Floor
from wohnflaechen.domain.entities.room import Room
from wohnflaechen.domain.enums.area_type import AreaType
from wohnflaechen.domain.enums.factor import Factor
from wohnflaechen.presentation.widgets.floor_sidebar_widget import MIME_ROOM_IDS

COL_NAME = 0
COL_NUMBER = 1
COL_AREA = 2
COL_FLOOR = 3
COL_AREA_TYPE = 4
COL_FACTOR = 5
COL_CALC = 6
COL_NOTE = 7

COMBO_COLUMNS = {COL_FLOOR, COL_AREA_TYPE, COL_FACTOR}

FLOOR_ROW_COLORS = [
    "#e8f4fc",
    "#eef0fa",
    "#e8f8f4",
    "#faf4ee",
    "#f0f2fa",
    "#f8f6ee",
    "#eef6f6",
    "#f6eef2",
]


class RoomDragTable(QTableWidget):
    """Tabelle mit Drag-Unterstützung für markierte Räume."""

    def __init__(self, pool: "RoomPoolWidget", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._pool = pool

    def startDrag(self, supportedActions) -> None:
        room_ids = self._pool.selected_room_ids()
        if not room_ids:
            return

        mime = QMimeData()
        mime.setData(MIME_ROOM_IDS, ",".join(str(rid) for rid in room_ids).encode("utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)


class RoomPoolWidget(QWidget):
    """Tabelle aller Räume mit Bearbeitung, Filter und Mehrfachaktionen."""

    rooms_changed = Signal()

    COLUMNS = [
        "Raumname",
        "Raumnummer",
        "Fläche (m²)",
        "Geschoss",
        "Flächenart",
        "Anrechnungsfaktor",
        "Berechnungsweg",
        "Bemerkung",
    ]

    def __init__(
        self,
        room_service: RoomService,
        floor_service: FloorService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._room_service = room_service
        self._floor_service = floor_service
        self._project_id: int | None = None
        self._rooms: list[Room] = []
        self._floors: list[Floor] = []
        self._filter_floor_id: int | None | str = None
        self._record_undo: Callable[[], None] | None = None
        self._build_ui()

    def set_undo_recorder(self, recorder: Callable[[], None] | None) -> None:
        self._record_undo = recorder

    def _snapshot_undo(self) -> None:
        if self._record_undo:
            self._record_undo()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.filter_label = QLabel("Alle Räume")
        self.filter_label.setObjectName("sectionTitle")
        header.addWidget(self.filter_label)
        header.addStretch()
        layout.addLayout(header)

        self.table = RoomDragTable(self, 0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setDragEnabled(True)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        bulk_row = QHBoxLayout()
        bulk_row.addWidget(QLabel("Auswahl:"))
        self.living_button = QPushButton("Wohnfläche")
        self.usable_button = QPushButton("Nutzfläche")
        self.none_button = QPushButton("Keine Flächenart")
        self.living_button.clicked.connect(lambda: self._bulk_area_type(AreaType.WOHNFLAECHE))
        self.usable_button.clicked.connect(lambda: self._bulk_area_type(AreaType.NUTZFLAECHE))
        self.none_button.clicked.connect(lambda: self._bulk_area_type(AreaType.NONE))
        bulk_row.addWidget(self.living_button)
        bulk_row.addWidget(self.usable_button)
        bulk_row.addWidget(self.none_button)
        bulk_row.addStretch()
        layout.addLayout(bulk_row)

        button_row = QHBoxLayout()
        self.add_button = QPushButton("Raum hinzufügen")
        self.delete_button = QPushButton("Raum löschen")
        self.add_button.clicked.connect(self._add_room)
        self.delete_button.clicked.connect(self._delete_rooms)
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.delete_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.cellClicked.connect(self._on_cell_clicked)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self._filter_floor_id = None
        self._filter_building_id = None
        self.filter_label.setText("Alle Räume")
        self.refresh()

    def set_building_filter(self, building_id: int | None) -> None:
        self._filter_building_id = building_id
        self.refresh()

    def set_floor_filter(self, floor_filter: int | None | str) -> None:
        self._filter_floor_id = floor_filter
        if floor_filter == "unassigned":
            self.filter_label.setText("Nicht zugeordnete Räume")
        elif floor_filter is None:
            self.filter_label.setText("Alle Räume")
        else:
            name = next((f.name for f in self._floors if f.id == floor_filter), "Geschoss")
            self.filter_label.setText(name)
        self.refresh()

    def refresh(self) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self._rooms = []
        self._floors = []

        if self._project_id is None:
            self.table.blockSignals(False)
            return

        all_rooms = self._room_service.list_rooms(self._project_id)
        self._floors = self._floor_service.list_floors(self._project_id)

        if self._filter_floor_id == "unassigned":
            self._rooms = [room for room in all_rooms if room.floor_id is None]
        elif self._filter_floor_id is not None:
            self._rooms = [room for room in all_rooms if room.floor_id == self._filter_floor_id]
        else:
            self._rooms = list(all_rooms)

        if self._filter_building_id is not None:
            self._rooms = [
                room for room in self._rooms if room.building_id == self._filter_building_id
            ]

        show_floor_colors = self._filter_floor_id is None
        self.table.setAlternatingRowColors(not show_floor_colors)

        for room in self._rooms:
            self._append_room_row(room)

        self.table.blockSignals(False)

    def get_rooms_for_summary(self) -> list[Room]:
        """Aktuelle Raumdaten inkl. ungespeicherter Tabellenänderungen."""
        if self._project_id is None:
            return []
        for row, room in enumerate(self._rooms):
            self._read_row(row, room)
        all_rooms = self._room_service.list_rooms(self._project_id)
        by_id = {room.id: room for room in all_rooms if room.id is not None}
        for room in self._rooms:
            if room.id is not None:
                by_id[room.id] = room
        return list(by_id.values())

    def selected_room_ids(self) -> list[int]:
        rows = sorted({index.row() for index in self.table.selectedIndexes()})
        ids: list[int] = []
        for row in rows:
            if 0 <= row < len(self._rooms) and self._rooms[row].id is not None:
                ids.append(self._rooms[row].id)
        return ids

    def assign_rooms_to_floor(self, floor_id: int | None, room_ids: list[int]) -> None:
        self._snapshot_undo()
        actual_floor_id = None if floor_id == -1 else floor_id
        self._room_service.assign_floor(room_ids, actual_floor_id)
        self.refresh()
        self.rooms_changed.emit()

    def save_all(self) -> None:
        if self._project_id is None:
            return
        all_rooms = self._room_service.list_rooms(self._project_id)
        id_to_row = {
            self._rooms[index].id: index
            for index in range(len(self._rooms))
            if self._rooms[index].id is not None
        }
        for room in all_rooms:
            row = id_to_row.get(room.id)
            if row is None:
                continue
            self._read_row(row, self._rooms[row])
            self._room_service.save_room(self._rooms[row])

    def _bulk_area_type(self, area_type: AreaType) -> None:
        room_ids = self.selected_room_ids()
        if not room_ids:
            QMessageBox.information(
                self,
                "Keine Auswahl",
                "Bitte mindestens einen Raum in der Tabelle markieren.",
            )
            return
        self._snapshot_undo()
        self._room_service.set_area_type_bulk(room_ids, area_type)
        self.refresh()
        self.rooms_changed.emit()

    def _append_room_row(self, room: Room) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        self._set_item(row, COL_NAME, room.name, editable=True)
        self._set_item(row, COL_NUMBER, room.number, editable=True)
        self._set_item(row, COL_AREA, f"{room.raw_area:.2f}", editable=True)
        self.table.setCellWidget(row, COL_FLOOR, self._create_floor_combo(room))
        self.table.setCellWidget(row, COL_AREA_TYPE, self._create_area_type_combo(room))
        self.table.setCellWidget(row, COL_FACTOR, self._create_factor_combo(room))
        self._set_item(row, COL_CALC, room.calculation_path, editable=True)
        self._set_item(row, COL_NOTE, room.note, editable=True)
        self._apply_row_floor_color(row, room)

    def _floor_color_map(self) -> dict[int, str]:
        mapping: dict[int, str] = {}
        for index, floor in enumerate(self._floors):
            if floor.id is not None:
                mapping[floor.id] = FLOOR_ROW_COLORS[index % len(FLOOR_ROW_COLORS)]
        return mapping

    def _apply_row_floor_color(self, row: int, room: Room) -> None:
        if self._filter_floor_id is not None:
            return
        color_hex = None
        if room.floor_id is not None:
            color_hex = self._floor_color_map().get(room.floor_id)
        if not color_hex:
            return

        color = QColor(color_hex)
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)
            widget = self.table.cellWidget(row, col)
            if isinstance(widget, QComboBox):
                widget.setStyleSheet(
                    f"QComboBox {{ background-color: {color_hex}; border: 1px solid #cdd9e8; }}"
                )

    def _set_item(self, row: int, col: int, text: str, editable: bool) -> None:
        item = QTableWidgetItem(text)
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, col, item)

    def _create_floor_combo(self, room: Room) -> QComboBox:
        combo = QComboBox()
        combo.addItem("—", None)
        for floor in self._floors:
            combo.addItem(floor.name, floor.id)
        self._set_combo_by_data(combo, room.floor_id)
        combo.currentIndexChanged.connect(self._on_floor_changed)
        return combo

    def _create_area_type_combo(self, room: Room) -> QComboBox:
        combo = QComboBox()
        combo.addItem("—", AreaType.NONE.value)
        for area_type in AreaType.choices():
            combo.addItem(area_type, area_type)
        self._set_combo_by_data(combo, room.area_type.value)
        combo.currentIndexChanged.connect(self._on_area_type_changed)
        return combo

    def _create_factor_combo(self, room: Room) -> QComboBox:
        combo = QComboBox()
        for factor in Factor:
            combo.addItem(factor.value, factor.value)
        self._set_combo_by_data(combo, room.factor.value)
        combo.currentIndexChanged.connect(self._on_factor_changed)
        return combo

    def _set_combo_by_data(self, combo: QComboBox, data) -> None:
        combo.blockSignals(True)
        index = combo.findData(data)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.blockSignals(False)

    def _combo_row(self, combo: QComboBox, column: int) -> int | None:
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, column) is combo:
                return row
        return None

    def _on_floor_changed(self, _index: int) -> None:
        combo = self.sender()
        if not isinstance(combo, QComboBox) or self.table.signalsBlocked():
            return
        row = self._combo_row(combo, COL_FLOOR)
        if row is None or row >= len(self._rooms):
            return
        self._snapshot_undo()
        room = self._rooms[row]
        room.floor_id = combo.currentData()
        self._update_area_display(row, room)
        self._room_service.save_room(room)
        self.rooms_changed.emit()

    def _on_area_type_changed(self, _index: int) -> None:
        combo = self.sender()
        if not isinstance(combo, QComboBox) or self.table.signalsBlocked():
            return
        row = self._combo_row(combo, COL_AREA_TYPE)
        if row is None or row >= len(self._rooms):
            return
        self._snapshot_undo()
        room = self._rooms[row]
        value = combo.currentData()
        room.area_type = AreaType(value) if value else AreaType.NONE
        self._room_service.save_room(room)
        self.rooms_changed.emit()

    def _on_factor_changed(self, _index: int) -> None:
        combo = self.sender()
        if not isinstance(combo, QComboBox) or self.table.signalsBlocked():
            return
        row = self._combo_row(combo, COL_FACTOR)
        if row is None or row >= len(self._rooms):
            return
        self._snapshot_undo()
        room = self._rooms[row]
        for factor in Factor:
            if factor.value == combo.currentData():
                room.factor = factor
                break
        self._room_service.save_room(room)
        self.rooms_changed.emit()

    def _on_cell_clicked(self, row: int, column: int) -> None:
        if column not in COMBO_COLUMNS:
            return
        widget = self.table.cellWidget(row, column)
        if isinstance(widget, QComboBox):
            widget.setFocus()
            widget.showPopup()

    def _on_cell_changed(self, row: int, column: int) -> None:
        if row >= len(self._rooms) or column in COMBO_COLUMNS:
            return
        self._snapshot_undo()
        room = self._rooms[row]
        item = self.table.item(row, column)
        if not item:
            return
        value = item.text().strip()

        if column == COL_NAME:
            room.name = value
        elif column == COL_NUMBER:
            room.number = value
        elif column == COL_AREA:
            try:
                room.raw_area = float(value.replace(",", "."))
            except ValueError:
                pass
        elif column == COL_CALC:
            room.calculation_path = value
        elif column == COL_NOTE:
            room.note = value

        self._update_area_display(row, room)
        self._room_service.save_room(room)
        self.rooms_changed.emit()

    def _update_area_display(self, row: int, room: Room) -> None:
        self.table.blockSignals(True)
        item = self.table.item(row, COL_AREA)
        if item:
            item.setText(f"{room.raw_area:.2f}")
        self.table.blockSignals(False)

    def _read_row(self, row: int, room: Room) -> None:
        for col in (COL_NAME, COL_NUMBER, COL_AREA, COL_CALC, COL_NOTE):
            item = self.table.item(row, col)
            if not item:
                continue
            value = item.text().strip()
            if col == COL_NAME:
                room.name = value
            elif col == COL_NUMBER:
                room.number = value
            elif col == COL_AREA:
                try:
                    room.raw_area = float(value.replace(",", "."))
                except ValueError:
                    pass
            elif col == COL_CALC:
                room.calculation_path = value
            elif col == COL_NOTE:
                room.note = value

        floor_combo = self.table.cellWidget(row, COL_FLOOR)
        if isinstance(floor_combo, QComboBox):
            room.floor_id = floor_combo.currentData()

        area_combo = self.table.cellWidget(row, COL_AREA_TYPE)
        if isinstance(area_combo, QComboBox):
            value = area_combo.currentData()
            room.area_type = AreaType(value) if value else AreaType.NONE

        factor_combo = self.table.cellWidget(row, COL_FACTOR)
        if isinstance(factor_combo, QComboBox):
            for factor in Factor:
                if factor.value == factor_combo.currentData():
                    room.factor = factor
                    break

    def _add_room(self) -> None:
        if self._project_id is None:
            return
        self._snapshot_undo()
        room = self._room_service.create_room(self._project_id)
        self._rooms.append(room)
        self._append_room_row(room)
        self.rooms_changed.emit()

    def _delete_rooms(self) -> None:
        rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        if not rows:
            return
        count = len(rows)
        confirm = QMessageBox.question(
            self,
            "Räume löschen",
            f"{count} Raum/Räume wirklich löschen?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._snapshot_undo()
        for row in rows:
            if row >= len(self._rooms):
                continue
            room = self._rooms[row]
            if room.id is not None:
                self._room_service.delete_room(room.id)
            self._rooms.pop(row)
            self.table.removeRow(row)
        self.rooms_changed.emit()
