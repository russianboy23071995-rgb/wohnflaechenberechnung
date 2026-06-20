"""Geschoss-Leiste mit Drag-and-Drop-Zuordnung."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.domain.entities.floor import Floor

MIME_ROOM_IDS = "application/x-wohnflaechen-room-ids"


class FloorDropList(QListWidget):
    """Geschossliste, die Raum-Drag-Drops annimmt."""

    rooms_dropped = Signal(int, list)  # floor_id (None as -1), room_ids

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat(MIME_ROOM_IDS):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(MIME_ROOM_IDS):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasFormat(MIME_ROOM_IDS):
            super().dropEvent(event)
            return

        item = self.itemAt(event.position().toPoint())
        if item is None:
            event.ignore()
            return

        floor_id = item.data(Qt.ItemDataRole.UserRole)
        raw = bytes(event.mimeData().data(MIME_ROOM_IDS)).decode("utf-8")
        room_ids = [int(part) for part in raw.split(",") if part.strip().isdigit()]
        if room_ids:
            self.rooms_dropped.emit(floor_id if floor_id is not None else -1, room_ids)
        event.acceptProposedAction()


class FloorSidebarWidget(QWidget):
    """Linke Leiste: Geschosse verwalten und Räume per Drag-and-Drop zuordnen."""

    floors_changed = Signal()
    rooms_assigned = Signal(int, list)  # floor_id or None (-1), room_ids
    filter_changed = Signal(object)  # floor_id or None or "unassigned"

    def __init__(self, floor_service: FloorService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._floor_service = floor_service
        self._project_id: int | None = None
        self._floors: list[Floor] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Geschosse")
        title.setStyleSheet("font-weight: 700; font-size: 11pt;")
        layout.addWidget(title)

        hint = QLabel("Markierte Räume hierher ziehen.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint)

        self.list_widget = FloorDropList()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        self.list_widget.rooms_dropped.connect(self._on_rooms_dropped)
        layout.addWidget(self.list_widget, stretch=1)

        button_row = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.add_button.setToolTip("Geschoss hinzufügen")
        self.rename_button = QPushButton("✎")
        self.rename_button.setToolTip("Geschoss umbenennen")
        self.delete_button = QPushButton("−")
        self.delete_button.setToolTip("Geschoss löschen")
        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")

        for btn in (
            self.add_button,
            self.rename_button,
            self.delete_button,
            self.up_button,
            self.down_button,
        ):
            btn.setMaximumWidth(36)
            button_row.addWidget(btn)

        self.add_button.clicked.connect(self._add_floor)
        self.rename_button.clicked.connect(self._rename_floor)
        self.delete_button.clicked.connect(self._delete_floor)
        self.up_button.clicked.connect(self._move_up)
        self.down_button.clicked.connect(self._move_down)
        layout.addLayout(button_row)

        unassigned_btn = QPushButton("Nicht zugeordnete Räume")
        unassigned_btn.clicked.connect(self._show_unassigned)
        layout.addWidget(unassigned_btn)

        show_all_btn = QPushButton("Alle Räume anzeigen")
        show_all_btn.clicked.connect(self._show_all)
        layout.addWidget(show_all_btn)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self._floors = []
        if self._project_id is None:
            self.list_widget.blockSignals(False)
            return

        self._floors = self._floor_service.list_floors(self._project_id)
        for floor in self._floors:
            item = QListWidgetItem(floor.name)
            item.setData(Qt.ItemDataRole.UserRole, floor.id)
            item.setToolTip("Räume hier ablegen")
            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

    def _on_rooms_dropped(self, floor_id: int, room_ids: list[int]) -> None:
        actual_floor_id = None if floor_id == -1 else floor_id
        self.rooms_assigned.emit(actual_floor_id if actual_floor_id is not None else -1, room_ids)

    def _on_selection_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._floors):
            return
        self.filter_changed.emit(self._floors[row].id)

    def _show_unassigned(self) -> None:
        self.list_widget.clearSelection()
        self.filter_changed.emit("unassigned")

    def _show_all(self) -> None:
        self.list_widget.clearSelection()
        self.filter_changed.emit(None)

    def _add_floor(self) -> None:
        if self._project_id is None:
            return
        name, ok = QInputDialog.getText(self, "Geschoss hinzufügen", "Geschossname:")
        if ok and name.strip():
            self._floor_service.create_floor(self._project_id, name.strip())
            self.refresh()
            self.floors_changed.emit()

    def _rename_floor(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return
        floor_id = item.data(Qt.ItemDataRole.UserRole)
        floor = self._floor_service.get_floor(floor_id)
        if not floor:
            return
        name, ok = QInputDialog.getText(
            self, "Geschoss bearbeiten", "Geschossname:", text=floor.name
        )
        if ok and name.strip():
            floor.name = name.strip()
            self._floor_service.update_floor(floor)
            self.refresh()
            self.floors_changed.emit()

    def _delete_floor(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return
        floor_id = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Geschoss löschen",
            "Dieses Geschoss wirklich löschen? Zugeordnete Räume werden freigegeben.",
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._floor_service.delete_floor(floor_id)
            self.refresh()
            self.floors_changed.emit()

    def _move_up(self) -> None:
        row = self.list_widget.currentRow()
        if row <= 0 or self._project_id is None:
            return
        self._floors[row], self._floors[row - 1] = self._floors[row - 1], self._floors[row]
        self._apply_order()

    def _move_down(self) -> None:
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self._floors) - 1 or self._project_id is None:
            return
        self._floors[row], self._floors[row + 1] = self._floors[row + 1], self._floors[row]
        self._apply_order()

    def _apply_order(self) -> None:
        if self._project_id is None:
            return
        floor_ids = [floor.id for floor in self._floors if floor.id is not None]
        self._floor_service.reorder_floors(self._project_id, floor_ids)
        self.refresh()
        self.floors_changed.emit()
