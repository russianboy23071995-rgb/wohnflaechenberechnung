"""Hauptfenster der Anwendung."""

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.app_context import AppContext
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.presentation.widgets.floor_sidebar_widget import FloorSidebarWidget
from wohnflaechen.presentation.widgets.new_project_wizard import NewProjectWizard
from wohnflaechen.presentation.widgets.preface_widget import PrefaceWidget
from wohnflaechen.presentation.widgets.project_dialog import ProjectDialog
from wohnflaechen.presentation.widgets.room_pool_widget import RoomPoolWidget
from wohnflaechen.presentation.widgets.summary_widget import SummaryWidget
from wohnflaechen.presentation.widgets.text_blocks_widget import TextBlocksWidget
from wohnflaechen.presentation.widgets.welcome_widget import WelcomeWidget


class MainWindow(QMainWindow):
    """Zentrale Arbeitsumgebung mit Willkommensbildschirm und einheitlicher Fläche."""

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._current_project: Project | None = None

        self.setWindowTitle("NOVIKOV | PLAN & MAß – Wohnflächenberechnung")
        self.setMinimumSize(1280, 760)

        self._build_menu()
        self._build_ui()
        self._show_welcome()

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Datei")
        self.new_action = QAction("Neue Berechnung …", self)
        self.open_action = QAction("Projekt öffnen …", self)
        self.save_action = QAction("Projekt speichern", self)
        self.import_action = QAction("Excel importieren (Archicad)", self)
        self.export_pdf_action = QAction("PDF exportieren", self)
        self.home_action = QAction("Startseite", self)
        self.quit_action = QAction("Beenden", self)

        self.new_action.triggered.connect(self._new_project_wizard)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.import_action.triggered.connect(self._import_excel)
        self.export_pdf_action.triggered.connect(self._export_pdf)
        self.home_action.triggered.connect(self._show_welcome)
        self.quit_action.triggered.connect(self.close)

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.import_action)
        file_menu.addAction(self.export_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.home_action)
        file_menu.addAction(self.quit_action)

        project_menu = menu_bar.addMenu("Projekt")
        self.edit_project_action = QAction("Projektdaten bearbeiten", self)
        self.preface_action = QAction("Vorbemerkungen bearbeiten …", self)
        self.text_blocks_action = QAction("Objekttexte bearbeiten …", self)
        self.edit_project_action.triggered.connect(self._edit_project)
        self.preface_action.triggered.connect(self._edit_preface)
        self.text_blocks_action.triggered.connect(self._edit_text_blocks)
        project_menu.addAction(self.edit_project_action)
        project_menu.addAction(self.preface_action)
        project_menu.addAction(self.text_blocks_action)

    def _build_ui(self) -> None:
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome = WelcomeWidget()
        self.welcome.create_project.connect(self._new_project_wizard)
        self.welcome.open_project.connect(self._open_project)
        self.stack.addWidget(self.welcome)

        self.workspace = QWidget()
        workspace_layout = QVBoxLayout(self.workspace)
        workspace_layout.setContentsMargins(8, 8, 8, 8)

        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        workspace_layout.addWidget(self.header_label)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        self.floor_sidebar = FloorSidebarWidget(self._context.floor_service)
        self.floor_sidebar.setMinimumWidth(200)
        self.floor_sidebar.setMaximumWidth(280)

        self.room_pool = RoomPoolWidget(
            self._context.room_service,
            self._context.floor_service,
        )

        self.summary = SummaryWidget(
            self._context.room_service,
            self._context.floor_service,
            self._context.calculation_service,
        )
        self.summary.setMinimumWidth(260)
        self.summary.setMaximumWidth(340)

        self.text_blocks = TextBlocksWidget(self._context.text_block_service)
        self.preface_editor = PrefaceWidget(self._context.text_block_service)

        splitter.addWidget(self.floor_sidebar)
        splitter.addWidget(self.room_pool)
        splitter.addWidget(self.summary)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 2)
        workspace_layout.addWidget(splitter, stretch=1)

        self.stack.addWidget(self.workspace)

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Bereit")

        self.floor_sidebar.floors_changed.connect(self._on_floors_changed)
        self.floor_sidebar.rooms_assigned.connect(self._on_rooms_assigned)
        self.floor_sidebar.filter_changed.connect(self.room_pool.set_floor_filter)
        self.room_pool.rooms_changed.connect(self._on_data_changed)
        self.summary.export_pdf_requested.connect(self._export_pdf)

    def _show_welcome(self) -> None:
        self.stack.setCurrentWidget(self.welcome)
        self.header_label.setText("")
        self._update_actions(has_project=False)

    def _show_workspace(self) -> None:
        self.stack.setCurrentWidget(self.workspace)
        self._update_project_state()

    def _update_actions(self, has_project: bool) -> None:
        self.save_action.setEnabled(has_project)
        self.import_action.setEnabled(has_project)
        self.export_pdf_action.setEnabled(has_project)
        self.edit_project_action.setEnabled(has_project)
        self.preface_action.setEnabled(has_project)
        self.text_blocks_action.setEnabled(has_project)
        self.summary.set_export_enabled(has_project)

    def _update_project_state(self) -> None:
        has_project = self._current_project is not None
        self._update_actions(has_project)

        if has_project and self._current_project:
            title = self._current_project.display_title()
            self.header_label.setText(title)
            self.setWindowTitle(f"NOVIKOV | PLAN & MAß – {title}")
            self.floor_sidebar.set_project(self._current_project.id)
            self.room_pool.set_project(self._current_project.id)
            self.text_blocks.set_project(self._current_project.id)
            self.preface_editor.set_project(self._current_project.id)
            self.summary.set_project(self._current_project.id)
        else:
            self.floor_sidebar.set_project(None)
            self.room_pool.set_project(None)
            self.text_blocks.set_project(None)
            self.preface_editor.set_project(None)
            self.summary.set_project(None)

    def _new_project_wizard(self) -> None:
        wizard = NewProjectWizard(self)
        if wizard.exec() != QDialog.DialogCode.Accepted:
            return

        project = wizard.get_project()
        created = self._context.project_service.create_project(project)
        self._current_project = created

        if created.id is not None:
            for name in wizard.get_floor_names():
                self._context.floor_service.create_floor(created.id, name)

            excel_path = wizard.get_excel_path()
            if excel_path:
                try:
                    result = self._context.import_service.import_excel(created.id, excel_path)
                    message = f"{result.imported_count} Räume importiert."
                    if result.warnings:
                        message += "\n" + "\n".join(result.warnings)
                    self.statusBar().showMessage(message, 5000)
                except Exception as exc:
                    QMessageBox.warning(
                        self,
                        "Import",
                        f"Projekt wurde angelegt, Excel-Import fehlgeschlagen:\n{exc}",
                    )

        self._show_workspace()
        self.statusBar().showMessage("Neue Berechnung gestartet", 3000)

    def _open_project(self) -> None:
        projects = self._context.project_service.list_projects()
        if not projects:
            QMessageBox.information(self, "Projekte", "Es sind noch keine Projekte vorhanden.")
            return

        labels = [
            f"{project.display_title()} "
            f"({project.created_at.strftime('%d.%m.%Y') if project.created_at else ''})"
            for project in projects
        ]
        choice, ok = QInputDialog.getItem(
            self, "Projekt öffnen", "Projekt auswählen:", labels, 0, False
        )
        if not ok:
            return
        index = labels.index(choice)
        self._current_project = projects[index]
        self._context.project_service.ensure_preface(self._current_project.id)
        self._show_workspace()
        self.statusBar().showMessage("Projekt geöffnet", 3000)

    def _edit_project(self) -> None:
        if not self._current_project:
            return
        dialog = ProjectDialog(self._current_project, parent=self)
        if dialog.exec() != ProjectDialog.DialogCode.Accepted:
            return
        updated = dialog.get_project()
        self._current_project = self._context.project_service.save_project(updated)
        self.text_blocks.refresh()
        self.preface_editor.refresh()
        self._update_project_state()
        self.statusBar().showMessage("Projektdaten aktualisiert", 3000)

    def _edit_preface(self) -> None:
        if not self._current_project:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Vorbemerkungen")
        dialog.setMinimumSize(720, 520)
        layout = QVBoxLayout(dialog)
        editor = PrefaceWidget(self._context.text_block_service)
        editor.set_project(self._current_project.id)
        layout.addWidget(editor)

        from PySide6.QtWidgets import QDialogButtonBox

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(lambda: (editor.save_all(), dialog.accept()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def _edit_text_blocks(self) -> None:
        if not self._current_project:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Objekttexte")
        dialog.setMinimumSize(720, 520)
        layout = QVBoxLayout(dialog)
        editor = TextBlocksWidget(self._context.text_block_service)
        editor.set_project(self._current_project.id)
        layout.addWidget(editor)

        from PySide6.QtWidgets import QDialogButtonBox

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(lambda: (editor.save_all(), dialog.accept()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def _save_project(self) -> None:
        if not self._current_project:
            return
        self.room_pool.save_all()
        self.text_blocks.save_all()
        self.preface_editor.save_all()
        self._current_project = self._context.project_service.save_project(self._current_project)
        self._on_data_changed()
        self.statusBar().showMessage("Projekt gespeichert", 3000)

    def _import_excel(self) -> None:
        if not self._current_project or self._current_project.id is None:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Archicad Excel importieren",
            "",
            "Excel-Dateien (*.xlsx *.xls)",
        )
        if not file_path:
            return

        try:
            result = self._context.import_service.import_excel(
                self._current_project.id,
                Path(file_path),
            )
        except Exception as exc:
            QMessageBox.critical(self, "Importfehler", str(exc))
            return

        message = f"{result.imported_count} Räume importiert."
        if result.new_floors:
            message += f"\nNeue Geschosse: {', '.join(result.new_floors)}"
        if result.warnings:
            message += "\n" + "\n".join(result.warnings)

        QMessageBox.information(self, "Import erfolgreich", message)
        self._on_floors_changed()

    def _export_pdf(self) -> None:
        if not self._current_project or self._current_project.id is None:
            return

        self.room_pool.save_all()
        self.text_blocks.save_all()
        self.preface_editor.save_all()

        default_name = self._current_project.display_title().replace("/", "-")
        default_path = f"{default_name} - WoFlV.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF exportieren",
            default_path,
            "PDF-Dateien (*.pdf)",
        )
        if not file_path:
            return

        try:
            document = self._context.document_export_service.build_document(
                self._current_project.id
            )
            self._context.pdf_engine.render_pdf(document, Path(file_path))
        except Exception as exc:
            QMessageBox.critical(
                self,
                "PDF-Exportfehler",
                f"Das PDF konnte nicht erzeugt werden:\n\n{exc}",
            )
            return

        self.statusBar().showMessage(f"PDF exportiert: {file_path}", 5000)
        QMessageBox.information(self, "PDF exportiert", f"Datei gespeichert:\n{file_path}")

    def _on_data_changed(self) -> None:
        rooms = self.room_pool.get_rooms_for_summary()
        self.summary.refresh(rooms)

    def _on_floors_changed(self) -> None:
        self.room_pool.refresh()
        self._on_data_changed()

    def _on_rooms_assigned(self, floor_id: int, room_ids: list[int]) -> None:
        actual_floor_id = None if floor_id == -1 else floor_id
        self.room_pool.assign_rooms_to_floor(actual_floor_id, room_ids)

    def closeEvent(self, event) -> None:
        if self._current_project:
            self.room_pool.save_all()
            self.text_blocks.save_all()
            self._context.project_service.save_project(self._current_project)
        self._context.connection.close()
        event.accept()
