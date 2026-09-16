"""Artboard-Ansicht: Pan, Zoom, PDFs platzieren."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from wohnflaechen.presentation.measure.canvas_items import PdfCanvasItem
from wohnflaechen.presentation.measure.pdf_loader import pdf_page_count, pdf_page_to_pixmap


class MeasureCanvasView(QGraphicsView):
    """Unendlicher Arbeitsbereich mit Raster und PDF-Elementen."""

    items_changed = Signal()

    GRID_STEP = 40

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self._scene.setSceneRect(-8000, -8000, 16000, 16000)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#e8e8e8")))
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

        self._panning = False
        self._pan_start = None
        self._pdf_items: list[PdfCanvasItem] = []

    def drawBackground(self, painter: QPainter, rect) -> None:
        super().drawBackground(painter, rect)
        step = self.GRID_STEP
        left = int(rect.left()) - (int(rect.left()) % step)
        top = int(rect.top()) - (int(rect.top()) % step)
        color = QColor("#d6d6d6")
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        x = left
        while x < rect.right():
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += step
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += step

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._panning and self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def add_pdf(self, file_path: Path, page_index: int = 0) -> PdfCanvasItem | None:
        try:
            pixmap = pdf_page_to_pixmap(file_path, page_index)
        except Exception:
            return None

        label = f"{file_path.name} · S. {page_index + 1}"
        item = PdfCanvasItem(pixmap, file_path, page_index, label)
        offset = len(self._pdf_items) * 48
        item.setPos(offset, offset)
        self._scene.addItem(item)
        self._pdf_items.append(item)
        self.items_changed.emit()
        return item

    def pdf_items(self) -> list[PdfCanvasItem]:
        return list(self._pdf_items)

    def clear_all(self) -> None:
        for item in self._pdf_items:
            self._scene.removeItem(item)
        self._pdf_items.clear()
        self.items_changed.emit()

    def zoom_fit(self) -> None:
        items = self._pdf_items
        if not items:
            self.resetTransform()
            return
        rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            rect = rect.united(item.sceneBoundingRect())
        self.fitInView(rect.adjusted(-80, -80, 80, 80), Qt.AspectRatioMode.KeepAspectRatio)

    def page_count(self, file_path: Path) -> int:
        try:
            return pdf_page_count(file_path)
        except Exception:
            return 0
