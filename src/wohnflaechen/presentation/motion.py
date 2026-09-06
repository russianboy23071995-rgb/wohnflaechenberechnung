"""Sanfte UI-Bewegungen – ein-/ausklappen und Ansichten verschieben.

Standard für alle künftigen Oberflächen-Elemente in dieser App:
Panels klappen weich auf/zu; Ansichten gleiten wie Blätter auf einem Tisch.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedLayout, QStackedWidget, QWidget

# Dauer & Kurven – einheitlich für das gesamte Produkt
EXPAND_DURATION_MS = 320
COLLAPSE_DURATION_MS = 260
VIEW_TRANSITION_DURATION_MS = 300
SIDE_SLIDE_DURATION_MS = 340

EASE_OUT = QEasingCurve.Type.OutCubic
EASE_IN = QEasingCurve.Type.InCubic
EASE_IN_OUT = QEasingCurve.Type.InOutCubic

_QWIDGETSIZE_MAX = 16777215


def _run_parallel_motion(
    parent: QWidget,
    animations: list[QPropertyAnimation],
    on_finished: Callable[[], None] | None = None,
) -> QParallelAnimationGroup:
    group = QParallelAnimationGroup(parent)
    for anim in animations:
        group.addAnimation(anim)
    if on_finished:
        group.finished.connect(on_finished)
    group.start()
    return group


class HeightMotionController:
    """Sanftes Auf- und Zuklappen über Höhe und Transparenz."""

    def __init__(self, widget: QWidget, max_expanded_height: int | None = None) -> None:
        self._widget = widget
        self._max_expanded_height = max_expanded_height
        self._expanded = False
        self._animating = False
        self._group: QParallelAnimationGroup | None = None

        self._opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(self._opacity_effect)

        widget.setMaximumHeight(0)
        self._opacity_effect.setOpacity(0.0)
        widget.show()

    def is_expanded(self) -> bool:
        return self._expanded

    def is_animating(self) -> bool:
        return self._animating

    def expand(self, on_finished: Callable[[], None] | None = None) -> None:
        if self._expanded and not self._animating:
            if on_finished:
                on_finished()
            return
        target = self._measure_expanded_height()
        start_h = self._widget.maximumHeight()
        start_o = float(self._opacity_effect.opacity())
        self._run(
            start_h,
            target,
            start_o,
            1.0,
            EXPAND_DURATION_MS,
            EASE_OUT,
            expanded=True,
            on_finished=on_finished,
        )

    def collapse(self, on_finished: Callable[[], None] | None = None) -> None:
        if not self._expanded and not self._animating:
            if on_finished:
                on_finished()
            return
        start_h = self._widget.maximumHeight()
        if start_h <= 0:
            start_h = self._measure_expanded_height()
        start_o = float(self._opacity_effect.opacity())
        self._run(
            start_h,
            0,
            start_o,
            0.0,
            COLLAPSE_DURATION_MS,
            EASE_IN,
            expanded=False,
            on_finished=on_finished,
        )

    def _measure_expanded_height(self) -> int:
        widget = self._widget
        widget.setMaximumHeight(_QWIDGETSIZE_MAX)
        widget.adjustSize()
        height = widget.sizeHint().height()
        if widget.layout():
            margins = widget.layout().contentsMargins()
            height += margins.top() + margins.bottom()
        widget.setMaximumHeight(0)
        height = max(height, 120)
        if self._max_expanded_height is not None:
            height = min(height, self._max_expanded_height)
        return height

    def _run(
        self,
        start_h: int,
        end_h: int,
        start_o: float,
        end_o: float,
        duration: int,
        easing: QEasingCurve.Type,
        expanded: bool,
        on_finished: Callable[[], None] | None,
    ) -> None:
        if self._group is not None:
            self._group.stop()
            self._group.deleteLater()
            self._group = None

        self._animating = True
        self._widget.show()

        height_anim = QPropertyAnimation(self._widget, b"maximumHeight")
        height_anim.setDuration(duration)
        height_anim.setEasingCurve(easing)
        height_anim.setStartValue(start_h)
        height_anim.setEndValue(end_h)

        opacity_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setEasingCurve(easing)
        opacity_anim.setStartValue(start_o)
        opacity_anim.setEndValue(end_o)

        def finished() -> None:
            self._animating = False
            self._expanded = expanded
            self._group = None
            if expanded:
                if self._max_expanded_height is not None:
                    self._widget.setMaximumHeight(self._max_expanded_height)
                else:
                    self._widget.setMaximumHeight(_QWIDGETSIZE_MAX)
                self._opacity_effect.setOpacity(1.0)
            else:
                self._widget.setMaximumHeight(0)
                self._opacity_effect.setOpacity(0.0)
            if on_finished:
                on_finished()

        self._group = _run_parallel_motion(
            self._widget,
            [height_anim, opacity_anim],
            finished,
        )


class WidthMotionController:
    """Seitenpanel – gleitet von rechts ins Dashboard."""

    def __init__(self, widget: QWidget, expanded_width: int) -> None:
        self._widget = widget
        self._expanded_width = expanded_width
        self._expanded = False
        self._animating = False
        self._group: QParallelAnimationGroup | None = None

        self._opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(self._opacity_effect)

        widget.setMaximumWidth(0)
        widget.setMinimumWidth(0)
        self._opacity_effect.setOpacity(0.0)
        widget.show()

    def is_expanded(self) -> bool:
        return self._expanded

    def is_animating(self) -> bool:
        return self._animating

    def expand(self, on_finished: Callable[[], None] | None = None) -> None:
        if self._expanded and not self._animating:
            if on_finished:
                on_finished()
            return
        start_w = self._widget.maximumWidth()
        start_o = float(self._opacity_effect.opacity())
        self._run(
            start_w,
            self._expanded_width,
            start_o,
            1.0,
            SIDE_SLIDE_DURATION_MS,
            EASE_OUT,
            expanded=True,
            on_finished=on_finished,
        )

    def collapse(self, on_finished: Callable[[], None] | None = None) -> None:
        if not self._expanded and not self._animating:
            if on_finished:
                on_finished()
            return
        start_w = self._widget.maximumWidth()
        if start_w <= 0:
            start_w = self._expanded_width
        start_o = float(self._opacity_effect.opacity())
        self._run(
            start_w,
            0,
            start_o,
            0.0,
            COLLAPSE_DURATION_MS,
            EASE_IN,
            expanded=False,
            on_finished=on_finished,
        )

    def toggle(self, on_finished: Callable[[], None] | None = None) -> None:
        if self.is_expanded() or self.is_animating():
            self.collapse(on_finished)
        else:
            self.expand(on_finished)

    def _run(
        self,
        start_w: int,
        end_w: int,
        start_o: float,
        end_o: float,
        duration: int,
        easing: QEasingCurve.Type,
        expanded: bool,
        on_finished: Callable[[], None] | None,
    ) -> None:
        if self._group is not None:
            self._group.stop()
            self._group.deleteLater()
            self._group = None

        self._animating = True
        self._widget.show()

        width_anim = QPropertyAnimation(self._widget, b"maximumWidth")
        width_anim.setDuration(duration)
        width_anim.setEasingCurve(easing)
        width_anim.setStartValue(start_w)
        width_anim.setEndValue(end_w)

        opacity_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        opacity_anim.setDuration(duration)
        opacity_anim.setEasingCurve(easing)
        opacity_anim.setStartValue(start_o)
        opacity_anim.setEndValue(end_o)

        def finished() -> None:
            self._animating = False
            self._expanded = expanded
            self._group = None
            if expanded:
                self._widget.setMaximumWidth(self._expanded_width)
                self._widget.setMinimumWidth(self._expanded_width)
                self._opacity_effect.setOpacity(1.0)
            else:
                self._widget.setMaximumWidth(0)
                self._widget.setMinimumWidth(0)
                self._opacity_effect.setOpacity(0.0)
            if on_finished:
                on_finished()

        self._group = _run_parallel_motion(
            self._widget,
            [width_anim, opacity_anim],
            finished,
        )


class StackViewAnimator:
    """Wechsel zwischen Hauptansichten – leichtes Gleiten wie Papier auf dem Tisch."""

    def __init__(self, stack: QStackedWidget) -> None:
        self._stack = stack
        self._running = False
        self._active_group: QParallelAnimationGroup | None = None

    def reset(self) -> None:
        """Alle Stack-Widgets zurücksetzen – verhindert Geister-Panels nach Navigation."""
        if self._active_group is not None:
            self._active_group.stop()
            self._active_group.deleteLater()
            self._active_group = None
        self._running = False

        layout = self._stack.layout()
        if isinstance(layout, QStackedLayout):
            layout.setStackingMode(QStackedLayout.StackingMode.StackOne)

        current = self._stack.currentWidget()
        for index in range(self._stack.count()):
            widget = self._stack.widget(index)
            widget.move(0, 0)
            widget.setGraphicsEffect(None)
            if widget is current:
                widget.show()
            else:
                widget.hide()

    def transition_to(
        self,
        widget: QWidget,
        forward: bool = True,
        *,
        full_slide: bool = False,
    ) -> None:
        current = self._stack.currentWidget()
        if current is widget:
            self.reset()
            return

        layout = self._stack.layout()
        if not isinstance(layout, QStackedLayout):
            self._stack.setCurrentWidget(widget)
            return

        if self._running:
            self.reset()
            self._stack.setCurrentWidget(widget)
            return

        index = self._stack.indexOf(widget)
        if index < 0:
            return

        self._running = True
        old_widget = current
        new_widget = widget

        if old_widget is None:
            self._stack.setCurrentWidget(new_widget)
            self._running = False
            return

        stack_width = self._stack.width()
        if stack_width < 48:
            parent = self._stack.parentWidget()
            while parent is not None and stack_width < 48:
                stack_width = parent.width()
                parent = parent.parentWidget()
        stack_width = max(stack_width, 48)
        slide = stack_width if full_slide else max(28, stack_width // 10)

        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self._stack.setCurrentIndex(index)

        rect = self._stack.rect()
        for i in range(self._stack.count()):
            page = self._stack.widget(i)
            if page is old_widget or page is new_widget:
                continue
            page.hide()
            page.move(0, 0)
            page.setGraphicsEffect(None)

        old_widget.move(0, 0)
        new_widget.move(0, 0)
        old_widget.setGeometry(rect)
        new_widget.setGeometry(rect)
        old_widget.show()
        new_widget.show()
        new_widget.raise_()

        start_new = QPoint(slide if forward else -slide, 0)
        end_old = QPoint(-slide if forward else slide, 0)

        anim_old = QPropertyAnimation(old_widget, b"pos")
        anim_old.setDuration(VIEW_TRANSITION_DURATION_MS)
        anim_old.setEasingCurve(EASE_IN_OUT)
        anim_old.setStartValue(QPoint(0, 0))
        anim_old.setEndValue(end_old)

        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setDuration(VIEW_TRANSITION_DURATION_MS)
        anim_new.setEasingCurve(EASE_IN_OUT)
        anim_new.setStartValue(start_new)
        anim_new.setEndValue(QPoint(0, 0))

        effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect)
        effect.setOpacity(0.35 if not full_slide else 0.85)

        old_effect = QGraphicsOpacityEffect(old_widget)
        old_widget.setGraphicsEffect(old_effect)

        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(VIEW_TRANSITION_DURATION_MS)
        fade_in.setEasingCurve(EASE_OUT)
        fade_in.setStartValue(0.35 if not full_slide else 0.85)
        fade_in.setEndValue(1.0)

        fade_out = QPropertyAnimation(old_effect, b"opacity")
        fade_out.setDuration(VIEW_TRANSITION_DURATION_MS)
        fade_out.setEasingCurve(EASE_IN)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0 if full_slide else 0.55)

        def cleanup() -> None:
            self._finalize_transition(old_widget, new_widget)
            self._active_group = None

        if self._active_group is not None:
            self._active_group.stop()
            self._active_group.deleteLater()

        self._active_group = _run_parallel_motion(
            self._stack,
            [anim_old, anim_new, fade_in, fade_out],
            cleanup,
        )

    def _finalize_transition(self, old_widget: QWidget, new_widget: QWidget) -> None:
        layout = self._stack.layout()
        if isinstance(layout, QStackedLayout):
            layout.setStackingMode(QStackedLayout.StackingMode.StackOne)

        for index in range(self._stack.count()):
            widget = self._stack.widget(index)
            widget.move(0, 0)
            widget.setGraphicsEffect(None)

        old_widget.hide()
        new_widget.show()
        new_widget.move(0, 0)
        new_widget.raise_()
        self._stack.setCurrentWidget(new_widget)
        self._running = False
