"""Persistente Shell: Ablage links, Dashboard / Auftragpanel / WoFlV, Profile rechts."""

from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QSizePolicy, QWidget

from wohnflaechen.application.services.folder_service import FolderService
from wohnflaechen.application.services.layout_settings_service import LayoutSettingsService
from wohnflaechen.presentation.dashboard_layout import (
    AUFTRAG_PANEL_MAX_WIDTH,
    AUFTRAG_PANEL_MIN_WIDTH,
    DASHBOARD_MAIN_MAX_WIDTH,
    DASHBOARD_MAIN_MIN_WIDTH,
)
from wohnflaechen.presentation.motion import StackViewAnimator
from wohnflaechen.presentation.widgets.client_profile_slide_panel import ClientProfileSlidePanel
from wohnflaechen.presentation.widgets.folder_nav_widget import FolderNavWidget
from wohnflaechen.presentation.widgets.resizable_width_panel import ResizableWidthPanel


class AppShellWidget(QWidget):
    """Navigation bleibt sichtbar; Mitte wechselt per Swipe."""

    def __init__(
        self,
        folder_service: FolderService,
        layout_settings: LayoutSettingsService,
        home_dashboard: QWidget,
        auftrag_panel: QWidget,
        workspace: QWidget,
        measure_workspace: QWidget,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appBackground")
        self._layout_settings = layout_settings
        self._hub_stack: QStackedWidget | None = None
        self._hub_animator: StackViewAnimator | None = None
        self._center_stack: QStackedWidget | None = None
        self._center_animator: StackViewAnimator | None = None
        self._hub_container: QWidget | None = None
        self._workspace = workspace
        self._measure_workspace = measure_workspace
        self._dashboard_resizable: ResizableWidthPanel | None = None
        self._auftrag_resizable: ResizableWidthPanel | None = None
        self._home_dashboard = home_dashboard
        self._auftrag_panel = auftrag_panel
        self._build_ui(folder_service)
        self._hub_animator = StackViewAnimator(self._hub_stack)
        self._center_animator = StackViewAnimator(self._center_stack)

    def _build_ui(self, folder_service: FolderService) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 24, 24, 24)
        root.setSpacing(12)

        self.folder_nav = FolderNavWidget(folder_service)
        self.folder_nav.setFixedWidth(248)
        root.addWidget(self.folder_nav)

        self._center_stack = QStackedWidget()

        self._hub_stack = QStackedWidget()

        self._dashboard_resizable = ResizableWidthPanel(
            self._home_dashboard,
            DASHBOARD_MAIN_MIN_WIDTH,
            DASHBOARD_MAIN_MAX_WIDTH,
            self._layout_settings.get_dashboard_width(),
        )
        self._dashboard_resizable.width_changed.connect(self._on_dashboard_width_changed)

        self._auftrag_resizable = ResizableWidthPanel(
            self._auftrag_panel,
            AUFTRAG_PANEL_MIN_WIDTH,
            AUFTRAG_PANEL_MAX_WIDTH,
            self._layout_settings.get_auftrag_panel_width(),
        )
        self._auftrag_resizable.width_changed.connect(self._on_auftrag_panel_width_changed)

        self._hub_stack.addWidget(self._dashboard_resizable)
        self._hub_stack.addWidget(self._auftrag_resizable)

        hub_row = QHBoxLayout()
        hub_row.setSpacing(0)
        hub_row.addWidget(self._hub_stack)
        hub_row.addStretch(1)

        self._hub_container = QWidget()
        self._hub_container.setLayout(hub_row)
        self._hub_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._center_stack.addWidget(self._hub_container)
        self._center_stack.addWidget(self._workspace)
        self._center_stack.addWidget(self._measure_workspace)

        root.addWidget(self._center_stack, stretch=1)

        self.client_profiles_panel = ClientProfileSlidePanel()
        root.addWidget(self.client_profiles_panel)

    def _on_dashboard_width_changed(self, width: int) -> None:
        self._layout_settings.set_dashboard_width(width)

    def _on_auftrag_panel_width_changed(self, width: int) -> None:
        self._layout_settings.set_auftrag_panel_width(width)

    def apply_saved_widths(self) -> None:
        if self._dashboard_resizable:
            self._dashboard_resizable.set_panel_width(self._layout_settings.get_dashboard_width())
        if self._auftrag_resizable:
            self._auftrag_resizable.set_panel_width(self._layout_settings.get_auftrag_panel_width())

    def show_hub(self, forward: bool = True) -> None:
        if self._center_animator and self._hub_container:
            self._center_animator.reset()
            self._center_animator.transition_to(self._hub_container, forward=forward)

    def show_measure_workspace(self, forward: bool = True) -> None:
        if self._center_animator and self._measure_workspace:
            self._center_animator.reset()
            self._center_animator.transition_to(self._measure_workspace, forward=forward)

    def show_workspace(self, forward: bool = True) -> None:
        if self._center_animator and self._workspace:
            self._center_animator.reset()
            self._center_animator.transition_to(self._workspace, forward=forward)

    def show_dashboard(self, forward: bool = False) -> None:
        if self._hub_animator and self._dashboard_resizable:
            self._hub_animator.reset()
            self._hub_animator.transition_to(self._dashboard_resizable, forward=not forward)

    def show_auftrag_panel(self, forward: bool = True) -> None:
        if self._hub_animator and self._auftrag_resizable:
            self._hub_animator.reset()
            self._hub_animator.transition_to(self._auftrag_resizable, forward=forward)

    def refresh_folder_nav(self) -> None:
        self.folder_nav.refresh()

    def is_on_workspace(self) -> bool:
        if self._center_stack is None:
            return False
        return self._center_stack.currentWidget() is self._workspace

    def is_on_measure_workspace(self) -> bool:
        if self._center_stack is None:
            return False
        return self._center_stack.currentWidget() is self._measure_workspace
