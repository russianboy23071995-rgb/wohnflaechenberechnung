"""Geschossverwaltung."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.services.floor_service import FloorService
from wohnflaechen.domain.entities.floor import Floor


class FloorManagerWidget(QWidget):
    """Liste und Reihenfolge der Geschosse."""

    floors_changed = Signal()

    def __init__(self, floor_service: FloorService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._floor_service = floor_service
        self._project_id: int | None = None
        self._floors: list[Floor] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.list_widget)

        button_row = QHBoxLayout()
        self.add_button = QPushButton("Geschoss hinzufügen")
        self.rename_button = QPushButton("Bearbeiten")
        self.delete_button = QPushButton("Löschen")
        self.up_button = QPushButton("Nach oben")
        self.down_button = QPushButton("Nach unten")

        self.add_button.clicked.connect(self._add_floor)
        self.rename_button.clicked.connect(self._rename_floor)
        self.delete_button.clicked.connect(self._delete_floor)
        self.up_button.clicked.connect(self._move_up)
        self.down_button.clicked.connect(self._move_down)

        button_row.addWidget(self.add_button)
        button_row.addWidget(self.rename_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.up_button)
        button_row.addWidget(self.down_button)
        layout.addLayout(button_row)

    def set_project(self, project_id: int | None) -> None:
        self._project_id = project_id
        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        self._floors = []
        if self._project_id is None:
            return

        self._floors = self._floor_service.list_floors(self._project_id)
        for floor in self._floors:
            item = QListWidgetItem(floor.name)
            item.setData(Qt.ItemDataRole.UserRole, floor.id)
            self.list_widget.addItem(item)

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
            "Dieses Geschoss wirklich löschen? Zugeordnete Räume verlieren die Geschosszuordnung.",
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
