"""Geschoss- und Gebäude-Leiste mit Drag-and-Drop-Zuordnung."""

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

from wohnflaechen.application.services.building_service import BuildingService
from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.domain.entities.building import Building
from wohnflaechen.domain.entities.floor import Floor

MIME_ROOM_IDS = "application/x-wohnflaechen-room-ids"


class FloorDropList(QListWidget):
    """Geschossliste, die Raum-Drag-Drops annimmt."""

    rooms_dropped = Signal(int, list)

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
    """Linke Leiste: Häuser, Geschosse, Raumzuordnung."""

    floors_changed = Signal()
    building_changed = Signal(object)
    rooms_assigned = Signal(int, list)
    filter_changed = Signal(object)

    def __init__(
        self,
        floor_service: FloorService,
        building_service: BuildingService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._floor_service = floor_service
        self._building_service = building_service
        self._project_id: int | None = None
        self._floors: list[Floor] = []
        self._buildings: list[Building] = []
        self._selected_building_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        building_title = QLabel("Häuser")
        building_title.setObjectName("sectionTitle")
        layout.addWidget(building_title)

        building_hint = QLabel("R- = Haus 1, E- = Haus 2 (automatisch beim Import).")
        building_hint.setObjectName("hintText")
        building_hint.setWordWrap(True)
        layout.addWidget(building_hint)

        self.building_list = QListWidget()
        self.building_list.setMaximumHeight(96)
        self.building_list.currentRowChanged.connect(self._on_building_selection_changed)
        layout.addWidget(self.building_list)

        building_buttons = QHBoxLayout()
        self.add_building_btn = QPushButton("+")
        self.add_building_btn.setToolTip("Haus hinzufügen")
        self.rename_building_btn = QPushButton("✎")
        self.rename_building_btn.setToolTip("Haus umbenennen")
        self.delete_building_btn = QPushButton("−")
        self.delete_building_btn.setToolTip("Haus löschen")
        for btn in (self.add_building_btn, self.rename_building_btn, self.delete_building_btn):
            btn.setObjectName("iconButton")
            btn.setMaximumWidth(40)
            building_buttons.addWidget(btn)
        building_buttons.addStretch()
        layout.addLayout(building_buttons)

        self.add_building_btn.clicked.connect(self._add_building)
        self.rename_building_btn.clicked.connect(self._rename_building)
        self.delete_building_btn.clicked.connect(self._delete_building)

        title = QLabel("Geschosse")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        hint = QLabel("Markierte Räume hierher ziehen.")
        hint.setObjectName("hintText")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.list_widget = FloorDropList()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.currentRowChanged.connect(self._on_floor_selection_changed)
        self.list_widget.rooms_dropped.connect(self._on_rooms_dropped)
        layout.addWidget(self.list_widget, stretch=1)

        button_row = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.rename_button = QPushButton("✎")
        self.delete_button = QPushButton("−")
        self.up_button = QPushButton("▲")
        self.down_button = QPushButton("▼")
        for btn in (
            self.add_button,
            self.rename_button,
            self.delete_button,
            self.up_button,
            self.down_button,
        ):
            btn.setObjectName("iconButton")
            btn.setMaximumWidth(40)
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
        self._selected_building_id = None
        self.refresh()

    def refresh(self) -> None:
        self._refresh_buildings()
        self._refresh_floors()

    def _refresh_buildings(self) -> None:
        self.building_list.blockSignals(True)
        self.building_list.clear()
        self._buildings = []
        if self._project_id is None:
            self.building_list.blockSignals(False)
            return

        self._buildings = self._building_service.list_buildings(self._project_id)
        all_item = QListWidgetItem("Alle Häuser")
        all_item.setData(Qt.ItemDataRole.UserRole, None)
        self.building_list.addItem(all_item)

        select_row = 0
        for index, building in enumerate(self._buildings, start=1):
            prefix = f" ({building.room_prefix})" if building.room_prefix else ""
            item = QListWidgetItem(f"{building.name}{prefix}")
            item.setData(Qt.ItemDataRole.UserRole, building.id)
            self.building_list.addItem(item)
            if building.id == self._selected_building_id:
                select_row = index

        self.building_list.setCurrentRow(select_row)
        self.building_list.blockSignals(False)
        if self._selected_building_id is None:
            self.building_changed.emit(None)

    def _refresh_floors(self) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self._floors = []
        if self._project_id is None:
            self.list_widget.blockSignals(False)
            return

        all_floors = self._floor_service.list_floors(self._project_id)
        if self._selected_building_id is None:
            self._floors = all_floors
        else:
            self._floors = [
                floor for floor in all_floors if floor.building_id == self._selected_building_id
            ]

        for floor in self._floors:
            item = QListWidgetItem(floor.name)
            item.setData(Qt.ItemDataRole.UserRole, floor.id)
            item.setToolTip("Räume hier ablegen")
            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

    def _on_building_selection_changed(self, row: int) -> None:
        if row < 0:
            return
        item = self.building_list.item(row)
        if item is None:
            return
        self._selected_building_id = item.data(Qt.ItemDataRole.UserRole)
        self._refresh_floors()
        self.building_changed.emit(self._selected_building_id)

    def _on_floor_selection_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._floors):
            return
        self.filter_changed.emit(self._floors[row].id)

    def _on_rooms_dropped(self, floor_id: int, room_ids: list[int]) -> None:
        actual_floor_id = None if floor_id == -1 else floor_id
        self.rooms_assigned.emit(actual_floor_id if actual_floor_id is not None else -1, room_ids)

    def _show_unassigned(self) -> None:
        self.list_widget.clearSelection()
        self.filter_changed.emit("unassigned")

    def _show_all(self) -> None:
        self.list_widget.clearSelection()
        self.filter_changed.emit(None)

    def _add_building(self) -> None:
        if self._project_id is None:
            return
        name, ok = QInputDialog.getText(self, "Haus hinzufügen", "Bezeichnung (z. B. Haus 1):")
        if not ok or not name.strip():
            return
        prefix, ok_prefix = QInputDialog.getText(
            self,
            "Raum-Präfix",
            "Präfix in Raumnummern (R oder E, leer = keins):",
        )
        if not ok_prefix:
            return
        building = self._building_service.create_building(
            self._project_id,
            name.strip(),
            prefix.strip().upper(),
        )
        self._selected_building_id = building.id
        self.refresh()
        self.floors_changed.emit()

    def _rename_building(self) -> None:
        item = self.building_list.currentItem()
        if not item or item.data(Qt.ItemDataRole.UserRole) is None:
            return
        building_id = item.data(Qt.ItemDataRole.UserRole)
        building = self._building_service.get_building(building_id)
        if not building:
            return
        name, ok = QInputDialog.getText(self, "Haus umbenennen", "Bezeichnung:", text=building.name)
        if ok and name.strip():
            building.name = name.strip()
            self._building_service.update_building(building)
            self.refresh()
            self.floors_changed.emit()

    def _delete_building(self) -> None:
        item = self.building_list.currentItem()
        if not item or item.data(Qt.ItemDataRole.UserRole) is None:
            return
        building_id = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Haus löschen",
            "Haus wirklich löschen? Geschosse bleiben ohne Haus-Zuordnung.",
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._building_service.delete_building(building_id)
            self._selected_building_id = None
            self.refresh()
            self.floors_changed.emit()

    def _add_floor(self) -> None:
        if self._project_id is None:
            return
        name, ok = QInputDialog.getText(self, "Geschoss hinzufügen", "Geschossname:")
        if ok and name.strip():
            self._floor_service.create_floor(
                self._project_id,
                name.strip(),
                building_id=self._selected_building_id,
            )
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
