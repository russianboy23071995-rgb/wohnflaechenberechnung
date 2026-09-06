"""Verschiebbare, skalierbare PDF-Elemente auf dem Canvas."""

from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem, QGraphicsRectItem

HANDLE_SIZE = 10.0


class _HandleKind(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class _ScaleHandle(QGraphicsRectItem):
    def __init__(self, kind: _HandleKind, parent_item: "PdfCanvasItem") -> None:
        super().__init__(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE, parent_item)
        self._kind = kind
        self._parent_item = parent_item
        self.setBrush(QBrush(QColor("#2e2e2e")))
        self.setPen(QPen(QColor("#ffffff"), 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self._dragging = False
        self._start_pos = QPointF()
        self._start_scale = 1.0

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_pos = event.scenePos()
            self._start_scale = self._parent_item.scale_factor()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            delta = event.scenePos() - self._start_pos
            self._parent_item.apply_scale_drag(self._kind, delta, self._start_scale)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)


class PdfCanvasItem(QGraphicsPixmapItem):
    """Eine PDF-Seite auf dem Artboard – verschiebbar und an den Ecken skalierbar."""

    def __init__(
        self,
        pixmap: QPixmap,
        source_path: Path,
        page_index: int,
        label: str,
    ) -> None:
        super().__init__(pixmap)
        self.source_path = source_path
        self.page_index = page_index
        self.label = label
        self._base_size = pixmap.size()
        self._scale_factor = 1.0
        self._handles: list[_ScaleHandle] = []
        self._updating_handles = False

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self._create_handles()

    def scale_factor(self) -> float:
        return self._scale_factor

    def set_scale_factor(self, factor: float) -> None:
        factor = max(0.05, min(8.0, factor))
        self._scale_factor = factor
        self.setScale(factor)
        self._sync_handles()

    def apply_scale_drag(self, kind: _HandleKind, delta: QPointF, start_scale: float) -> None:
        base_w = max(self._base_size.width(), 1)
        base_h = max(self._base_size.height(), 1)
        if kind in (_HandleKind.TOP_RIGHT, _HandleKind.BOTTOM_RIGHT):
            scale_delta = delta.x() / base_w
        else:
            scale_delta = -delta.x() / base_w
        if kind in (_HandleKind.BOTTOM_LEFT, _HandleKind.BOTTOM_RIGHT):
            scale_delta = (scale_delta + delta.y() / base_h) / 2
        else:
            scale_delta = (scale_delta - delta.y() / base_h) / 2
        self.set_scale_factor(start_scale + scale_delta)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            visible = bool(value)
            for handle in self._handles:
                handle.setVisible(visible)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._sync_handles()
        return super().itemChange(change, value)

    def _create_handles(self) -> None:
        for kind in _HandleKind:
            handle = _ScaleHandle(kind, self)
            handle.setVisible(False)
            self._handles.append(handle)
        self._sync_handles()

    def _sync_handles(self) -> None:
        if self._updating_handles:
            return
        self._updating_handles = True
        rect = self.boundingRect()
        positions = {
            _HandleKind.TOP_LEFT: rect.topLeft(),
            _HandleKind.TOP_RIGHT: rect.topRight(),
            _HandleKind.BOTTOM_LEFT: rect.bottomLeft(),
            _HandleKind.BOTTOM_RIGHT: rect.bottomRight(),
        }
        for handle in self._handles:
            handle.setPos(positions[handle._kind])
        self._updating_handles = False
