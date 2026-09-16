"""Panel mit Griff zum Ändern der Breite per Maus."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

from wohnflaechen.presentation.dashboard_layout import (
    DASHBOARD_MAIN_MAX_WIDTH,
    DASHBOARD_MAIN_MIN_WIDTH,
)


class _ResizeGrip(QFrame):
    def __init__(self, parent_panel: "ResizableWidthPanel") -> None:
        super().__init__(parent_panel)
        self._panel = parent_panel
        self.setObjectName("resizeGrip")
        self.setFixedWidth(10)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self._dragging = False
        self._start_x = 0
        self._start_width = 0

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_x = int(event.globalPosition().x())
            self._start_width = self._panel.panel_width()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            delta = int(event.globalPosition().x()) - self._start_x
            self._panel.set_panel_width(self._start_width + delta)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._panel.emit_width_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class ResizableWidthPanel(QWidget):
    width_changed = Signal(int)

    def __init__(
        self,
        content: QWidget,
        min_width: int = DASHBOARD_MAIN_MIN_WIDTH,
        max_width: int = DASHBOARD_MAIN_MAX_WIDTH,
        initial_width: int = 720,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._min_width = min_width
        self._max_width = max_width
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(content, stretch=1)
        self._grip = _ResizeGrip(self)
        layout.addWidget(self._grip)

        self.set_panel_width(initial_width)

    def panel_width(self) -> int:
        return self.width()

    def set_panel_width(self, width: int) -> None:
        clamped = max(self._min_width, min(self._max_width, width))
        self.setFixedWidth(clamped)

    def emit_width_changed(self) -> None:
        self.width_changed.emit(self.panel_width())
