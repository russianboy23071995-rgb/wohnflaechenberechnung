"""Auftraggeber-Profiliste – gleitet von rechts ins Dashboard."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.domain.entities.client_profile import ClientProfile
from wohnflaechen.presentation.motion import WidthMotionController

PANEL_WIDTH = 340


class ClientProfileSlidePanel(QFrame):
    """Interaktive Profilliste am rechten Rand."""

    profile_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidePanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._profiles: list[ClientProfile] = []
        self._motion = WidthMotionController(self, PANEL_WIDTH)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Auftraggeber")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()
        close_btn = QPushButton("Schließen")
        close_btn.setObjectName("ghostButton")
        close_btn.clicked.connect(self.collapse)
        header.addWidget(close_btn)
        layout.addLayout(header)

        hint = QLabel(
            "Wiederkehrende Kunden – ein Klick übernimmt Name, Adresse, "
            "E-Mail und Telefon ins Formular."
        )
        hint.setObjectName("hintText")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("dashboardScroll")
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()

        self.empty_label = QLabel("Noch keine Profile – nach dem ersten Auftrag erscheinen Kunden hier.")
        self.empty_label.setObjectName("hintText")
        self.empty_label.setWordWrap(True)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll.setWidget(self.list_container)
        layout.addWidget(self.scroll, stretch=1)

    def set_profiles(self, profiles: list[ClientProfile]) -> None:
        self._profiles = profiles
        self._rebuild_list()

    def expand(self) -> None:
        self._motion.expand()

    def collapse(self) -> None:
        self._motion.collapse()

    def toggle(self) -> None:
        self._motion.toggle()

    def is_expanded(self) -> bool:
        return self._motion.is_expanded()

    def _rebuild_list(self) -> None:
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget and widget is not self.empty_label:
                widget.deleteLater()

        if not self._profiles:
            self.empty_label.setVisible(True)
            if self.empty_label.parent() is None:
                self.list_layout.insertWidget(0, self.empty_label)
            return

        self.empty_label.setVisible(False)
        if self.empty_label.parent() is not None:
            self.list_layout.removeWidget(self.empty_label)
            self.empty_label.hide()

        for profile in self._profiles:
            btn = QPushButton()
            btn.setObjectName("profileCardButton")
            btn.setMinimumHeight(52)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            label = profile.display_label()
            sub = profile.subtitle()
            btn.setText(f"{label}\n{sub}" if sub else label)
            btn.clicked.connect(lambda _checked=False, p=profile: self._on_pick(p))
            self.list_layout.insertWidget(self.list_layout.count() - 1, btn)

    def _on_pick(self, profile: ClientProfile) -> None:
        self.profile_selected.emit(profile)
        self.collapse()
