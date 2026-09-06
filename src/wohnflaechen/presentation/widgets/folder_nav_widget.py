"""Linke Navigation – Ordnerstruktur."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.services.folder_service import FolderService
from wohnflaechen.domain.entities.folder import Folder


class FolderNavWidget(QFrame):
    """Baumansicht für Vorgänge, Kunden, Objekte, Angebote, Rechnungen."""

    folder_selected = Signal(object, object)  # category str | None, folder_id int | None
    create_subfolder_requested = Signal(int)  # parent folder id

    def __init__(self, folder_service: FolderService, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._service = folder_service
        self._folders: list[Folder] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Ablage")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()
        refresh_btn = QPushButton("↻")
        refresh_btn.setObjectName("ghostButton")
        refresh_btn.setFixedWidth(32)
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        hint = QLabel("Ordner für Kunden, Objekte und Dokumente.")
        hint.setObjectName("hintText")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setObjectName("folderTree")
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.tree, stretch=1)

        self.new_folder_btn = QPushButton("Neuer Unterordner")
        self.new_folder_btn.setObjectName("secondaryButton")
        self.new_folder_btn.clicked.connect(self._on_new_subfolder)
        layout.addWidget(self.new_folder_btn)

    def refresh(self) -> None:
        self._folders = self._service.list_folders()
        self.tree.clear()
        roots = [f for f in self._folders if f.parent_id is None]
        item_map: dict[int, QTreeWidgetItem] = {}
        for folder in roots:
            item = QTreeWidgetItem([folder.name])
            item.setData(0, Qt.ItemDataRole.UserRole, folder.id)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, folder.category)
            self.tree.addTopLevelItem(item)
            item_map[folder.id] = item

        for folder in self._folders:
            if folder.parent_id is None or folder.id is None:
                continue
            parent_item = item_map.get(folder.parent_id)
            if parent_item is None:
                continue
            item = QTreeWidgetItem([folder.name])
            item.setData(0, Qt.ItemDataRole.UserRole, folder.id)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, folder.category)
            parent_item.addChild(item)
            item_map[folder.id] = item

        self.tree.expandAll()

    def _on_selection_changed(self) -> None:
        item = self.tree.currentItem()
        if item is None:
            self.folder_selected.emit(None, None)
            return
        folder_id = item.data(0, Qt.ItemDataRole.UserRole)
        category = item.data(0, Qt.ItemDataRole.UserRole + 1)
        self.folder_selected.emit(category, folder_id)

    def _on_new_subfolder(self) -> None:
        item = self.tree.currentItem()
        if item is None:
            return
        folder_id = item.data(0, Qt.ItemDataRole.UserRole)
        if folder_id is not None:
            self.create_subfolder_requested.emit(int(folder_id))

    def _on_context_menu(self, pos) -> None:
        item = self.tree.itemAt(pos)
        if item is None:
            return
        folder_id = item.data(0, Qt.ItemDataRole.UserRole)
        if folder_id is None:
            return
        menu = QMenu(self)
        menu.addAction("Neuer Unterordner", lambda: self.create_subfolder_requested.emit(int(folder_id)))
        menu.exec(self.tree.mapToGlobal(pos))
