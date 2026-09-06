"""Hauptfenster der Anwendung."""

from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.application.app_context import AppContext
from wohnflaechen.application.dto.dashboard_entry import DashboardEntry
from wohnflaechen.application.services.document_storage_service import DocumentStorageService
from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.presentation.widgets.app_shell_widget import AppShellWidget
from wohnflaechen.presentation.widgets.auftrag_dashboard_widget import AuftragDashboardWidget
from wohnflaechen.presentation.widgets.auftrag_dialog import AuftragDialog
from wohnflaechen.presentation.widgets.invoice_dialog import InvoiceDialog
from wohnflaechen.presentation.widgets.pdf_export_dialog import PdfExportDialog
from wohnflaechen.presentation.widgets.settings_dialog import SettingsDialog
from wohnflaechen.presentation.widgets.woflv_from_auftrag_wizard import WoflvFromAuftragWizard
from wohnflaechen.presentation.widgets.floor_sidebar_widget import FloorSidebarWidget
from wohnflaechen.presentation.widgets.new_project_wizard import NewProjectWizard
from wohnflaechen.presentation.widgets.preface_widget import PrefaceWidget
from wohnflaechen.presentation.widgets.project_dialog import ProjectDialog
from wohnflaechen.presentation.widgets.room_pool_widget import RoomPoolWidget
from wohnflaechen.presentation.widgets.summary_widget import SummaryWidget
from wohnflaechen.presentation.widgets.text_blocks_widget import TextBlocksWidget
from wohnflaechen.presentation.widgets.measure_workspace_widget import MeasureWorkspaceWidget
from wohnflaechen.presentation.ui_utils import open_export_location
from wohnflaechen.presentation.pdf.weasyprint_support import (
    PdfExportNotAvailableError,
    check_pdf_export_available,
)


class MainWindow(QMainWindow):
    """Zentrale Arbeitsumgebung mit Willkommensbildschirm und einheitlicher Fläche."""

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self._context = context
        self._current_project: Project | None = None
        self._current_auftrag: Auftrag | None = None
        self._last_pdf_export_path: Path | None = None

        self.setWindowTitle("NOVIKOV | PLAN & MAß – Auftragsverwaltung")
        self.setMinimumSize(1100, 720)
        self.setObjectName("appBackground")

        self._build_menu()
        self._build_ui()
        self._show_home()

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Datei")
        self.new_action = QAction("Neue Berechnung …", self)
        self.open_action = QAction("Projekt öffnen …", self)
        self.save_action = QAction("Projekt speichern", self)
        self.import_action = QAction("Excel importieren (Archicad)", self)
        self.export_pdf_action = QAction("PDF exportieren", self)
        self.home_action = QAction("Dashboard", self)
        self.quit_action = QAction("Beenden", self)

        self.new_action.triggered.connect(self._new_project_wizard)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.import_action.triggered.connect(self._import_excel)
        self.export_pdf_action.triggered.connect(self._export_pdf)
        self.home_action.triggered.connect(self._go_home)
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

        settings_menu = menu_bar.addMenu("Einstellungen")
        self.settings_action = QAction("Dokumentenablage …", self)
        self.settings_action.triggered.connect(self._open_settings)
        settings_menu.addAction(self.settings_action)

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

        help_menu = menu_bar.addMenu("Hilfe")
        self.check_pdf_action = QAction("PDF-Export prüfen …", self)
        self.check_pdf_action.triggered.connect(self._check_pdf_export)
        help_menu.addAction(self.check_pdf_action)

        edit_menu = menu_bar.addMenu("Bearbeiten")
        self.undo_action = QAction("Rückgängig", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self._undo_room_change)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)

    def _build_ui(self) -> None:
        self.home_dashboard = HomeDashboardWidget(self._context.client_profile_service)
        self.home_dashboard.auftrag_submitted.connect(self._on_dashboard_auftrag_submitted)
        self.home_dashboard.woflv_only_requested.connect(self._new_project_wizard)
        self.home_dashboard.settings_requested.connect(self._open_settings)
        self.home_dashboard.open_hub.connect(self._open_hub_from_dashboard)
        self.home_dashboard.open_offer.connect(self._open_offer_from_dashboard)
        self.home_dashboard.open_woflv.connect(self._open_woflv_from_dashboard)
        self.home_dashboard.open_invoice.connect(self._open_invoice_from_dashboard)
        self.home_dashboard.toggle_completed.connect(self._toggle_entry_completed)
        self.home_dashboard.move_to_folder.connect(self._move_entry_to_folder)
        self.home_dashboard.profile_picker_requested.connect(self._toggle_client_profiles)

        self.auftrag_dashboard = AuftragDashboardWidget()
        self.auftrag_dashboard.edit_auftrag_requested.connect(self._edit_auftrag)
        self.auftrag_dashboard.offer_requested.connect(self._handle_offer)
        self.auftrag_dashboard.woflv_requested.connect(self._start_woflv_from_auftrag)
        self.auftrag_dashboard.woflv_open_requested.connect(self._open_woflv_from_auftrag)
        self.auftrag_dashboard.measure_requested.connect(self._open_measure_from_auftrag)
        self.auftrag_dashboard.invoice_requested.connect(self._handle_invoice)
        self.auftrag_dashboard.back_requested.connect(self._show_home)

        self.workspace = QWidget()
        self.workspace.setObjectName("appBackground")
        workspace_layout = QVBoxLayout(self.workspace)
        workspace_layout.setContentsMargins(16, 12, 16, 16)
        workspace_layout.setSpacing(12)

        self.header_label = QLabel()
        self.header_label.setObjectName("headerTitle")
        workspace_layout.addWidget(self.header_label)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        self.floor_sidebar = FloorSidebarWidget(
            self._context.floor_service,
            self._context.building_service,
        )
        self.floor_sidebar.setObjectName("glassPanel")
        self.floor_sidebar.setMinimumWidth(200)
        self.floor_sidebar.setMaximumWidth(280)

        self.room_pool = RoomPoolWidget(
            self._context.room_service,
            self._context.floor_service,
        )
        self.room_pool.setObjectName("glassPanel")
        self.room_pool.set_undo_recorder(self._record_room_undo)

        self.summary = SummaryWidget(
            self._context.room_service,
            self._context.floor_service,
            self._context.calculation_service,
        )
        self.summary.setObjectName("glassPanel")
        self.summary.setMinimumWidth(300)
        self.summary.setMaximumWidth(390)

        self.text_blocks = TextBlocksWidget(self._context.text_block_service)
        self.preface_editor = PrefaceWidget(self._context.text_block_service)

        splitter.addWidget(self.floor_sidebar)
        splitter.addWidget(self.room_pool)
        splitter.addWidget(self.summary)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)
        workspace_layout.addWidget(splitter, stretch=1)

        self.measure_workspace = MeasureWorkspaceWidget()
        self.measure_workspace.back_requested.connect(self._back_from_measure)

        self.shell = AppShellWidget(
            self._context.folder_service,
            self._context.layout_settings_service,
            self.home_dashboard,
            self.auftrag_dashboard,
            self.workspace,
            self.measure_workspace,
        )
        self.setCentralWidget(self.shell)

        self.shell.folder_nav.folder_selected.connect(self._on_folder_nav_selected)
        self.shell.folder_nav.create_subfolder_requested.connect(self._create_subfolder)
        self.shell.client_profiles_panel.profile_selected.connect(
            self.home_dashboard.apply_client_profile
        )

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Bereit")

        self.floor_sidebar.floors_changed.connect(self._on_floors_changed)
        self.floor_sidebar.building_changed.connect(self.room_pool.set_building_filter)
        self.floor_sidebar.rooms_assigned.connect(self._on_rooms_assigned)
        self.floor_sidebar.filter_changed.connect(self.room_pool.set_floor_filter)
        self.room_pool.rooms_changed.connect(self._on_data_changed)
        self.summary.export_pdf_requested.connect(self._export_pdf)
        self.summary.open_export_folder_requested.connect(self._open_last_export_folder)
        self.summary.continue_to_invoice_requested.connect(self._continue_to_invoice_from_woflv)

    def _go_home(self) -> None:
        self._show_home()

    def _show_home(self) -> None:
        self._current_auftrag = None
        self._current_project = None
        self.home_dashboard.collapse_all_panels()
        self.home_dashboard.set_entries(self._load_dashboard_entries())
        self._refresh_client_profiles()
        if self.shell.is_on_workspace() or self.shell.is_on_measure_workspace():
            self.shell.show_hub(forward=False)
        self.shell.show_dashboard(forward=False)
        self.header_label.setText("")
        self._update_actions(has_project=False)

    def _load_dashboard_entries(self) -> list[DashboardEntry]:
        entries: list[DashboardEntry] = []
        for auftrag in self._context.auftrag_service.list_auftraege():
            if auftrag.id is None:
                continue
            aid = auftrag.id
            offer = self._context.offer_service.get_offer(aid)
            invoice = self._context.invoice_service.get_invoice(aid)
            project = self._context.auftrag_service.get_woflv_project(aid)
            entries.append(
                DashboardEntry(
                    key=f"auftrag-{aid}",
                    title=auftrag.display_title(),
                    client=auftrag.client_name,
                    object_address=auftrag.object_address,
                    created_at=auftrag.created_at,
                    auftrag_id=aid,
                    project_id=project.id if project else None,
                    has_offer=offer is not None,
                    has_woflv=project is not None,
                    has_invoice=invoice is not None,
                    offer_number=offer.number if offer else "",
                    invoice_number=invoice.number if invoice else "",
                    completed=auftrag.completed,
                )
            )
        for project in self._context.project_service.list_projects():
            if project.auftrag_id is not None or project.id is None:
                continue
            entries.append(
                DashboardEntry(
                    key=f"project-{project.id}",
                    title=project.display_title(),
                    client=project.client,
                    object_address=project.address,
                    created_at=project.created_at,
                    project_id=project.id,
                    has_woflv=True,
                    completed=project.completed,
                )
            )
        entries.sort(
            key=lambda e: e.created_at or datetime.min,
            reverse=True,
        )
        return entries

    def _get_dashboard_entry(self, key: str) -> DashboardEntry | None:
        for entry in self._load_dashboard_entries():
            if entry.key == key:
                return entry
        return None

    def _toggle_entry_completed(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if entry is None:
            return
        new_state = not entry.completed
        if entry.auftrag_id is not None:
            self._context.auftrag_service.set_auftrag_completed(entry.auftrag_id, new_state)
        elif entry.project_id is not None:
            self._context.project_service.set_project_completed(entry.project_id, new_state)
        self.home_dashboard.set_entries(self._load_dashboard_entries())

    def _on_folder_nav_selected(self, category, folder_id) -> None:
        keys: set[str] = set()
        title = "Ihre Vorgänge"
        if folder_id is not None:
            folder = self._context.folder_service.get_folder(folder_id)
            if folder:
                title = folder.name
            keys = self._context.folder_service.folder_item_keys(folder_id)
        self.home_dashboard.set_folder_filter(category, folder_id, keys, title)
        if self.shell.is_on_workspace() or self.shell.is_on_measure_workspace():
            self.shell.show_hub(forward=False)
        self.shell.show_dashboard(forward=False)

    def _refresh_client_profiles(self) -> None:
        profiles = self._context.client_profile_service.list_profiles()
        self.shell.client_profiles_panel.set_profiles(profiles)

    def _toggle_client_profiles(self) -> None:
        panel = self.shell.client_profiles_panel
        if panel.is_expanded():
            panel.collapse()
        else:
            self._refresh_client_profiles()
            panel.expand()

    def _move_entry_to_folder(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if entry is None:
            return
        folders = self._context.folder_service.list_folders()
        if not folders:
            QMessageBox.information(self, "Ordner", "Keine Ordner vorhanden.")
            return
        labels = [f.name for f in folders]
        folder_map = {f.name: f for f in folders}
        choice, ok = QInputDialog.getItem(
            self,
            "In Ordner verschieben",
            "Zielordner:",
            labels,
            0,
            False,
        )
        if not ok:
            return
        folder = folder_map[choice]
        if folder.id is None:
            return
        if entry.auftrag_id is not None:
            self._context.folder_service.move_item(folder.id, "auftrag", entry.auftrag_id)
        elif entry.project_id is not None:
            self._context.folder_service.move_item(folder.id, "project", entry.project_id)
        self.shell.refresh_folder_nav()
        self.statusBar().showMessage(f"Verschoben nach „{folder.name}“", 3000)

    def _create_subfolder(self, parent_id: int) -> None:
        name, ok = QInputDialog.getText(self, "Neuer Unterordner", "Name:")
        if not ok or not name.strip():
            return
        try:
            self._context.folder_service.create_subfolder(parent_id, name.strip())
        except ValueError as exc:
            QMessageBox.warning(self, "Ordner", str(exc))
            return
        self.shell.refresh_folder_nav()
        self.statusBar().showMessage("Unterordner erstellt", 3000)

    def _record_room_undo(self) -> None:
        if self._current_project and self._current_project.id is not None:
            self._context.room_undo_service.record(self._current_project.id)
            self._update_undo_action()

    def _undo_room_change(self) -> None:
        if not self._current_project or self._current_project.id is None:
            return
        project_id = self._current_project.id
        if self._context.room_undo_service.undo(project_id):
            self.room_pool.refresh()
            self._on_data_changed()
            self.statusBar().showMessage("Rückgängig", 2500)
        self._update_undo_action()

    def _update_undo_action(self) -> None:
        enabled = False
        if self._current_project and self._current_project.id is not None:
            enabled = self._context.room_undo_service.can_undo(self._current_project.id)
        self.undo_action.setEnabled(enabled)

    def _open_hub_from_dashboard(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if not entry or entry.auftrag_id is None:
            return
        self._current_auftrag = self._context.auftrag_service.get_auftrag(entry.auftrag_id)
        self._show_auftrag_dashboard()

    def _open_offer_from_dashboard(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if not entry or entry.auftrag_id is None:
            return
        self._current_auftrag = self._context.auftrag_service.get_auftrag(entry.auftrag_id)
        self._handle_offer()

    def _open_invoice_from_dashboard(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if not entry or entry.auftrag_id is None:
            return
        self._current_auftrag = self._context.auftrag_service.get_auftrag(entry.auftrag_id)
        self._handle_invoice()

    def _open_woflv_from_dashboard(self, key: str) -> None:
        entry = self._get_dashboard_entry(key)
        if entry is None:
            return
        if entry.project_id is not None:
            self._current_project = self._context.project_service.get_project(entry.project_id)
            if entry.auftrag_id is not None:
                self._current_auftrag = self._context.auftrag_service.get_auftrag(entry.auftrag_id)
            if self._current_project:
                self._context.project_service.ensure_preface(self._current_project.id)
                self._show_workspace()
            return
        if entry.auftrag_id is not None:
            self._current_auftrag = self._context.auftrag_service.get_auftrag(entry.auftrag_id)
            project = self._context.auftrag_service.get_woflv_project(entry.auftrag_id)
            if project:
                self._current_project = project
                self._context.project_service.ensure_preface(project.id)
                self._show_workspace()
            else:
                self._start_woflv_from_auftrag()

    def _on_dashboard_auftrag_submitted(self, auftrag, follow_up: str = "") -> None:
        if auftrag.id is not None:
            saved = self._context.auftrag_service.save_auftrag(auftrag)
        else:
            saved = self._context.auftrag_service.create_auftrag(auftrag)
        self._current_auftrag = saved
        self._context.client_profile_service.remember_from_auftrag(
            saved.client_name,
            saved.client_address,
            saved.client_email,
            saved.client_phone,
        )
        self.home_dashboard.set_entries(self._load_dashboard_entries())
        self._refresh_client_profiles()
        if follow_up == "offer":
            self._handle_offer()
            self.statusBar().showMessage("Auftrag angelegt – Angebot", 3000)
        elif follow_up == "invoice":
            self._handle_invoice()
            self.statusBar().showMessage("Auftrag angelegt – Rechnung", 3000)
        else:
            self._show_auftrag_dashboard()
            self.statusBar().showMessage("Auftrag angelegt", 3000)

    def _new_auftrag_for_offer(self) -> None:
        self._show_home()
        self.home_dashboard.expand_auftrag_panel("offer")

    def _new_auftrag_for_invoice(self) -> None:
        self._show_home()
        self.home_dashboard.expand_auftrag_panel("invoice")

    def _show_welcome(self) -> None:
        self._show_home()

    def _show_auftrag_dashboard(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        self._refresh_auftrag_dashboard()
        if self.shell.is_on_workspace() or self.shell.is_on_measure_workspace():
            self.shell.show_hub(forward=True)
        self.shell.show_auftrag_panel(forward=True)
        self.header_label.setText("")
        self._update_actions(has_project=False)

    def _refresh_auftrag_dashboard(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        aid = self._current_auftrag.id
        offer = self._context.offer_service.get_offer(aid)
        invoice = self._context.invoice_service.get_invoice(aid)
        project = self._context.auftrag_service.get_woflv_project(aid)
        self.auftrag_dashboard.refresh(self._current_auftrag, offer, project, invoice)

    def _open_settings(self) -> None:
        root = self._context.document_storage_service.get_documents_root()
        dialog = SettingsDialog(str(root) if root else "", parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if dialog.restore_layout_requested():
            self._context.layout_settings_service.restore_defaults()
            self.shell.apply_saved_widths()
            self.statusBar().showMessage("Standardansicht wiederhergestellt", 4000)
        path_text = dialog.documents_root()
        if not path_text:
            QMessageBox.warning(self, "Einstellungen", "Bitte einen gültigen Ordner angeben.")
            return
        path = Path(path_text)
        if not path.is_dir():
            QMessageBox.warning(self, "Einstellungen", "Der Ordner existiert nicht.")
            return
        self._context.document_storage_service.set_documents_root(path)
        self.statusBar().showMessage(f"Dokumentenablage: {path}", 5000)

    def _new_auftrag(self) -> None:
        self._show_home()
        self.home_dashboard.show_new_auftrag_panel()

    def _open_auftrag(self) -> None:
        auftraege = self._context.auftrag_service.list_auftraege()
        if not auftraege:
            QMessageBox.information(self, "Aufträge", "Es sind noch keine Aufträge vorhanden.")
            return
        labels = [
            f"{a.display_title()} ({a.created_at.strftime('%d.%m.%Y') if a.created_at else ''})"
            for a in auftraege
        ]
        choice, ok = QInputDialog.getItem(self, "Auftrag öffnen", "Auftrag auswählen:", labels, 0, False)
        if not ok:
            return
        self._current_auftrag = auftraege[labels.index(choice)]
        self._show_auftrag_dashboard()
        self.statusBar().showMessage("Auftrag geöffnet", 3000)

    def _edit_auftrag(self) -> None:
        if not self._current_auftrag:
            return
        dialog = AuftragDialog(self._current_auftrag, parent=self)
        if dialog.exec() != AuftragDialog.DialogCode.Accepted:
            return
        self._current_auftrag = self._context.auftrag_service.save_auftrag(dialog.get_auftrag())
        self._refresh_auftrag_dashboard()

    def _handle_offer(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        aid = self._current_auftrag.id
        offer = self._context.offer_service.get_offer(aid)
        if offer is None:
            offer = self._context.offer_service.create_default_offer(aid)
        dialog = OfferDialog(offer, parent=self)
        if dialog.exec() != OfferDialog.DialogCode.Accepted:
            return
        offer = dialog.get_offer()
        try:
            path = self._context.document_storage_service.default_offer_path(
                self._current_auftrag, offer
            )
            self._context.commercial_pdf_engine.render_offer(
                self._current_auftrag, offer, path
            )
            offer.file_path = str(path)
        except ValueError as exc:
            QMessageBox.warning(self, "Ablagepfad", str(exc))
            return
        except PdfExportNotAvailableError as exc:
            QMessageBox.critical(self, "PDF-Export nicht verfügbar", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "PDF-Fehler", f"Angebot-PDF konnte nicht erstellt werden:\n{exc}")
            return
        self._context.offer_service.save_offer(offer)
        self._refresh_auftrag_dashboard()
        self.home_dashboard.set_entries(self._load_dashboard_entries())
        QMessageBox.information(self, "Angebot", f"Angebot gespeichert:\n{offer.file_path}")

    def _handle_invoice(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        aid = self._current_auftrag.id
        invoice = self._context.invoice_service.get_invoice(aid)
        offer = self._context.offer_service.get_offer(aid)
        if invoice is None:
            invoice = self._context.invoice_service.create_from_offer(aid, offer)
        dialog = InvoiceDialog(invoice, parent=self)
        if dialog.exec() != InvoiceDialog.DialogCode.Accepted:
            return
        invoice = dialog.get_invoice()
        try:
            path = self._context.document_storage_service.default_invoice_path(
                self._current_auftrag, invoice
            )
            self._context.commercial_pdf_engine.render_invoice(
                self._current_auftrag, invoice, path
            )
            invoice.file_path = str(path)
        except ValueError as exc:
            QMessageBox.warning(self, "Ablagepfad", str(exc))
            return
        except PdfExportNotAvailableError as exc:
            QMessageBox.critical(self, "PDF-Export nicht verfügbar", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "PDF-Fehler", f"Rechnungs-PDF konnte nicht erstellt werden:\n{exc}")
            return
        self._context.invoice_service.save_invoice(invoice)
        self._refresh_auftrag_dashboard()
        self.home_dashboard.set_entries(self._load_dashboard_entries())
        QMessageBox.information(self, "Rechnung", f"Rechnung gespeichert:\n{invoice.file_path}")

    def _start_woflv_from_auftrag(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        existing = self._context.auftrag_service.get_woflv_project(self._current_auftrag.id)
        if existing:
            QMessageBox.information(
                self,
                "WoFlV",
                "Für diesen Auftrag existiert bereits eine Berechnung. "
                "Nutzen Sie „WoFlV öffnen“.",
            )
            return
        project = self._context.auftrag_service.project_from_auftrag(self._current_auftrag)
        wizard = WoflvFromAuftragWizard(self._current_auftrag, project, parent=self)
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
                    self.statusBar().showMessage(f"{result.imported_count} Räume importiert", 5000)
                except Exception as exc:
                    QMessageBox.warning(self, "Import", f"Excel-Import fehlgeschlagen:\n{exc}")
        self._show_workspace()
        self.statusBar().showMessage("Wohnflächenberechnung gestartet", 3000)

    def _open_woflv_from_auftrag(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            return
        project = self._context.auftrag_service.get_woflv_project(self._current_auftrag.id)
        if not project:
            QMessageBox.information(self, "WoFlV", "Noch keine Berechnung für diesen Auftrag.")
            return
        self._current_project = project
        self._context.project_service.ensure_preface(project.id)
        self._show_workspace()

    def _open_measure_from_auftrag(self) -> None:
        if not self._current_auftrag:
            return
        self.measure_workspace.set_auftrag(self._current_auftrag)
        self.shell.show_measure_workspace(forward=True)
        self.statusBar().showMessage("Maß-Canvas geöffnet", 3000)

    def _back_from_measure(self) -> None:
        if not self._current_auftrag or self._current_auftrag.id is None:
            self._show_home()
            return
        self.shell.show_hub(forward=False)
        self._show_auftrag_dashboard()

    def _show_workspace(self) -> None:
        self.shell.show_workspace(forward=True)
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
            self.setWindowTitle(f"NOVIKOV | PLAN & Maß – {title}")
            if self._current_project.auftrag_id is not None:
                self._current_auftrag = self._context.auftrag_service.get_auftrag(
                    self._current_project.auftrag_id
                )
            pdf_path = self._current_project.file_path.strip()
            if pdf_path:
                self._last_pdf_export_path = Path(pdf_path)
                self.summary.set_export_folder_available(True)
                self.summary.set_continue_to_invoice_available(self._can_create_invoice())
            else:
                self._last_pdf_export_path = None
                self.summary.set_export_folder_available(False)
                self.summary.set_continue_to_invoice_available(False)
            self.floor_sidebar.set_project(self._current_project.id)
            self.room_pool.set_project(self._current_project.id)
            self.text_blocks.set_project(self._current_project.id)
            self.preface_editor.set_project(self._current_project.id)
            self.summary.set_project(self._current_project.id)
            self._update_undo_action()
        else:
            self._last_pdf_export_path = None
            self.floor_sidebar.set_project(None)
            self.room_pool.set_project(None)
            self.text_blocks.set_project(None)
            self.preface_editor.set_project(None)
            self.summary.set_project(None)
            self._update_undo_action()

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
        if self._current_auftrag:
            self._refresh_auftrag_dashboard()
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
        if result.new_buildings:
            message += f"\nNeue Häuser: {', '.join(result.new_buildings)}"
        if result.warnings:
            message += "\n" + "\n".join(result.warnings)

        QMessageBox.information(self, "Import erfolgreich", message)
        self._on_floors_changed()

    def _ensure_current_auftrag(self) -> bool:
        if self._current_auftrag and self._current_auftrag.id is not None:
            return True
        if self._current_project and self._current_project.auftrag_id is not None:
            self._current_auftrag = self._context.auftrag_service.get_auftrag(
                self._current_project.auftrag_id
            )
        return self._current_auftrag is not None and self._current_auftrag.id is not None

    def _can_create_invoice(self) -> bool:
        return self._ensure_current_auftrag()

    def _continue_to_invoice_from_woflv(self) -> None:
        if not self._ensure_current_auftrag():
            QMessageBox.information(
                self,
                "Rechnung",
                "Für dieses Projekt ist kein Auftrag verknüpft. "
                "Rechnungen können nur über einen Auftrag erstellt werden.",
            )
            return
        self._handle_invoice()

    def _export_pdf(self) -> None:
        if not self._current_project or self._current_project.id is None:
            return

        self.room_pool.save_all()
        self.text_blocks.save_all()
        self.preface_editor.save_all()

        output_path: Path | None = None
        if self._current_auftrag:
            try:
                output_path = self._context.document_storage_service.default_woflv_path(
                    self._current_auftrag,
                    self._current_project,
                )
            except ValueError:
                output_path = None

        if output_path is None:
            default_name = self._current_project.display_title().replace("/", "-")
            suggested = f"{default_name} - WoFlV.pdf"
            root = self._context.document_storage_service.get_documents_root()
            if root:
                suggested = str(
                    root / DocumentStorageService.SUBDIR_WOFLV / suggested
                )
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF exportieren",
                suggested,
                "PDF-Dateien (*.pdf)",
            )
            if not file_path:
                return
            output_path = Path(file_path)

        layout_dialog = PdfExportDialog(parent=self)
        if layout_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        pdf_layout = layout_dialog.selected_layout()

        try:
            document = self._context.document_export_service.build_document(
                self._current_project.id
            )
            self._context.pdf_engine.render_pdf(document, output_path, layout=pdf_layout)
        except PdfExportNotAvailableError as exc:
            QMessageBox.critical(
                self,
                "PDF-Export nicht verfügbar",
                str(exc),
            )
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                "PDF-Exportfehler",
                f"Das PDF konnte nicht erzeugt werden:\n\n{type(exc).__name__}: {exc}",
            )
            return

        self._current_project.file_path = str(output_path)
        self._context.project_service.save_project(self._current_project)

        self.statusBar().showMessage(f"PDF exportiert: {output_path}", 5000)
        self._last_pdf_export_path = output_path
        self.summary.set_export_folder_available(True)
        self.summary.set_continue_to_invoice_available(self._can_create_invoice())

        message = QMessageBox(self)
        message.setIcon(QMessageBox.Icon.Information)
        message.setWindowTitle("PDF exportiert")
        message.setText(f"Datei gespeichert:\n{output_path}")
        open_folder_button = message.addButton(
            "Ordner öffnen",
            QMessageBox.ButtonRole.ActionRole,
        )
        message.addButton(QMessageBox.StandardButton.Ok)
        message.exec()
        if message.clickedButton() == open_folder_button:
            self._open_last_export_folder()

    def _open_last_export_folder(self) -> None:
        if self._last_pdf_export_path is None:
            return
        open_export_location(self._last_pdf_export_path)

    def _check_pdf_export(self) -> None:
        ok, detail = check_pdf_export_available()
        if ok:
            QMessageBox.information(self, "PDF-Export", detail)
        else:
            QMessageBox.warning(self, "PDF-Export nicht verfügbar", detail)

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
