"""Eingeklapptes Auftragsformular – Schritte mit Weiter/Zurück."""

from collections.abc import Callable

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.presentation.motion import HeightMotionController
from wohnflaechen.presentation.widgets.auftrag_form_widget import AuftragFormWidget


class AuftragInlinePanel(QFrame):
    submitted = Signal(object, str)
    cancelled = Signal()
    profile_picker_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("inlinePanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._follow_up = ""
        self._editing: Auftrag | None = None
        self._motion = HeightMotionController(self)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self.title_label = QLabel("Neuer Auftrag")
        self.title_label.setObjectName("sectionTitle")
        header.addWidget(self.title_label)
        header.addStretch()
        self.step_indicator = QLabel("Schritt 1 von 3")
        self.step_indicator.setObjectName("hintText")
        header.addWidget(self.step_indicator)
        collapse_btn = QPushButton("Schließen")
        collapse_btn.setObjectName("ghostButton")
        collapse_btn.clicked.connect(self.collapse)
        header.addWidget(collapse_btn)
        layout.addLayout(header)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("hintText")
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        self.form = AuftragFormWidget()
        self.form.profile_picker_requested.connect(self.profile_picker_requested.emit)
        layout.addWidget(self.form)

        nav = QHBoxLayout()
        self.back_btn = QPushButton("Zurück")
        self.back_btn.setObjectName("ghostButton")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.clicked.connect(self._on_back)
        self.next_btn = QPushButton("Weiter")
        self.next_btn.setObjectName("secondaryButton")
        self.next_btn.setMinimumHeight(40)
        self.next_btn.clicked.connect(self._on_next)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.setObjectName("ghostButton")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.save_btn = QPushButton("Auftrag speichern")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self._on_save)
        nav.addWidget(self.back_btn)
        nav.addWidget(self.next_btn)
        nav.addStretch()
        nav.addWidget(self.cancel_btn)
        nav.addWidget(self.save_btn)
        layout.addLayout(nav)
        self._sync_nav()

    def _sync_nav(self) -> None:
        step = self.form.current_step() + 1
        self.step_indicator.setText(f"Schritt {step} von 3")
        self.back_btn.setEnabled(self.form.current_step() > 0)
        on_last = self.form.is_last_step()
        self.next_btn.setVisible(not on_last)
        self.save_btn.setVisible(on_last)
        if self._follow_up == "offer" and on_last:
            self.save_btn.setText("Speichern & Angebot erstellen")
        elif self._follow_up == "invoice" and on_last:
            self.save_btn.setText("Speichern & Rechnung erstellen")
        elif on_last:
            self.save_btn.setText("Auftrag speichern")

    def _prepare_new(self, follow_up: str = "") -> None:
        self._follow_up = follow_up
        self._editing = None
        self.title_label.setText("Neuer Auftrag")
        if follow_up == "offer":
            self.subtitle_label.setText(
                "Schrittweise erfassen – danach öffnet sich direkt das Angebot."
            )
        elif follow_up == "invoice":
            self.subtitle_label.setText(
                "Schrittweise erfassen – danach öffnet sich direkt die Rechnung."
            )
        else:
            self.subtitle_label.setText(
                "Erfassen Sie Auftraggeber, Objekt und Bearbeitung in drei Schritten."
            )
        self.form.clear_form()
        self.form._apply_step_layout()
        self._sync_nav()

    def expand_new(self, follow_up: str = "") -> None:
        self._prepare_new(follow_up)
        if self.is_expanded():
            self._focus_first_field()
            return
        self._motion.expand(self._focus_first_field)

    def expand_edit(self, auftrag: Auftrag) -> None:
        self._follow_up = ""
        self._editing = auftrag
        self.title_label.setText("Auftrag bearbeiten")
        self.subtitle_label.setText("Stammdaten in Schritten aktualisieren.")
        self.save_btn.setText("Änderungen speichern")
        self.form.load_auftrag(auftrag)
        self._sync_nav()
        self._motion.expand(self._focus_first_field)

    def collapse(self, on_finished: Callable[[], None] | None = None) -> None:
        def done() -> None:
            self._follow_up = ""
            self._editing = None
            self.form.reset_steps()
            self._sync_nav()
            if on_finished:
                on_finished()

        self._motion.collapse(done)

    def is_expanded(self) -> bool:
        return self._motion.is_expanded()

    def toggle_new(self) -> None:
        if self.is_expanded() and self._editing is None and not self._follow_up:
            self.collapse()
        else:
            self.expand_new()

    def apply_client_profile(self, profile) -> None:
        self.form.apply_client_profile(profile)

    def _focus_first_field(self) -> None:
        self.form._apply_step_layout()
        QTimer.singleShot(0, self.form.focus_current_step)

    def _on_back(self) -> None:
        if self.form.go_back():
            self._sync_nav()
            self.form.focus_current_step()

    def _on_next(self) -> None:
        error = self.form.validate_step(self.form.current_step())
        if error:
            QMessageBox.warning(self, "Pflichtfeld", error)
            return
        if self.form.go_next():
            self._sync_nav()
            self.form.focus_current_step()

    def _on_cancel(self) -> None:
        self.collapse(self.cancelled.emit)

    def _on_save(self) -> None:
        error = self.form.validate()
        if error:
            QMessageBox.warning(self, "Pflichtfeld", error)
            return
        auftrag = self.form.build_auftrag(self._editing)
        follow_up = self._follow_up

        def emit_submitted() -> None:
            self.submitted.emit(auftrag, follow_up)

        self.collapse(emit_submitted)
