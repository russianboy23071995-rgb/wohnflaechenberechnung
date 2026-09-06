"""Mehrstufiges Auftragsformular mit horizontalen Übergängen."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.client_profile import ClientProfile
from wohnflaechen.presentation.motion import StackViewAnimator


class _ClippedStepHost(QWidget):
    """Feste Höhe – Schritte gleiten innerhalb eines festen Bereichs."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("wizardStepHost")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def set_step_height(self, height: int) -> None:
        self.setFixedHeight(height)


class AuftragFormWidget(QWidget):
    """Drei Schritte: Auftraggeber → Objekt → Bearbeitung."""

    profile_picker_requested = Signal()
    STEP_COUNT = 3

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._step = 0
        self._step_host = _ClippedStepHost()
        self._stack = QStackedWidget(self._step_host)
        self._animator = StackViewAnimator(self._stack)
        self._step_widgets: list[QWidget] = []
        self._build_ui()
        self._apply_step_layout()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        host_layout = QVBoxLayout(self._step_host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)
        host_layout.addWidget(self._stack)

        self._step_widgets = [
            self._build_client_step(),
            self._build_object_step(),
            self._build_meta_step(),
        ]
        for step in self._step_widgets:
            self._stack.addWidget(step)

        layout.addWidget(self._step_host)

    def _build_client_step(self) -> QWidget:
        box = self._group_shell(
            "Auftrag & Auftraggeber",
            "Projektname und Kundendaten für Angebot und Rechnung.",
        )
        form = QFormLayout()
        form.setSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title_edit = self._line_field(form, "Projektname / Kurzbezeichnung", "title")
        self.client_name_edit = self._line_field(form, "Auftraggeber", "client_name")
        self.client_address_edit = self._line_field(form, "Adresse Auftraggeber", "client_address")
        self.client_email_edit = self._line_field(form, "E-Mail", "client_email")
        self.client_phone_edit = self._line_field(form, "Telefon", "client_phone")
        box.layout().addLayout(form)

        picker_row = QHBoxLayout()
        picker_row.addStretch()
        profile_btn = QPushButton("Aus Profilliste wählen")
        profile_btn.setObjectName("secondaryButton")
        profile_btn.setMinimumHeight(36)
        profile_btn.clicked.connect(self.profile_picker_requested.emit)
        picker_row.addWidget(profile_btn)
        box.layout().addLayout(picker_row)
        return box

    def _build_object_step(self) -> QWidget:
        box = self._group_shell(
            "Objekt",
            "Bezogene Immobilie oder Bauvorhaben.",
        )
        form = QFormLayout()
        form.setSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.object_name_edit = self._line_field(form, "Objektbezeichnung", "object_name")
        self.object_address_edit = self._line_field(form, "Objektadresse", "object_address")
        box.layout().addLayout(form)
        return box

    def _build_meta_step(self) -> QWidget:
        box = self._group_shell(
            "Bearbeitung",
            "Optional – für PDFs und interne Zuordnung.",
        )
        form = QFormLayout()
        form.setSpacing(10)
        self.editor_edit = self._line_field(form, "Bearbeiter", "editor")
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(88)
        self.notes_edit.setMaximumHeight(88)
        self.notes_edit.setPlaceholderText("Interne Hinweise …")
        form.addRow("Notizen", self.notes_edit)
        box.layout().addLayout(form)
        return box

    def _group_shell(self, title: str, hint: str) -> QFrame:
        box = QFrame()
        box.setObjectName("formGroup")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(18, 16, 18, 16)
        box_layout.setSpacing(10)
        head = QLabel(title)
        head.setObjectName("formGroupTitle")
        box_layout.addWidget(head)
        sub = QLabel(hint)
        sub.setObjectName("hintText")
        sub.setWordWrap(True)
        box_layout.addWidget(sub)
        return box

    def _line_field(self, form: QFormLayout, label: str, attr: str) -> QLineEdit:
        edit = QLineEdit()
        edit.setMinimumHeight(40)
        edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if attr == "object_name":
            edit.setPlaceholderText("z. B. Wohnung EG links")
        elif attr == "client_name":
            edit.setPlaceholderText("Name oder Firma")
        elif attr == "title":
            edit.setPlaceholderText("z. B. Heckscherstraße 33 – WHG 1")
        form.addRow(label, edit)
        return edit

    def _measure_width(self) -> int:
        width = self.width()
        if width > 0:
            return width
        parent = self.parentWidget()
        if parent and parent.width() > 0:
            return parent.width()
        return 560

    def _step_content_height(self, widget: QWidget, width: int) -> int:
        widget.ensurePolished()
        hint = widget.sizeHint().height()
        for_width = widget.heightForWidth(width)
        if for_width > 0:
            hint = max(hint, for_width)
        widget.adjustSize()
        hint = max(hint, widget.height())
        return hint

    def _max_step_height(self) -> int:
        width = self._measure_width()
        heights = [self._step_content_height(step, width) for step in self._step_widgets]
        return max(max(heights, default=280), 280)

    def _apply_step_layout(self) -> None:
        height = self._max_step_height()
        self._step_host.set_step_height(height)
        self._stack.setFixedHeight(height)
        for step in self._step_widgets:
            step.setMinimumHeight(height)
            step.setMaximumHeight(height)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self._apply_step_layout()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_step_layout()

    def required_height(self) -> int:
        return self._max_step_height()

    def current_step(self) -> int:
        return self._step

    def is_last_step(self) -> bool:
        return self._step >= self.STEP_COUNT - 1

    def reset_steps(self) -> None:
        self._step = 0
        self._animator.reset()
        self._stack.setCurrentIndex(0)
        self._apply_step_layout()

    def go_next(self) -> bool:
        error = self.validate_step(self._step)
        if error:
            return False
        if self._step >= self.STEP_COUNT - 1:
            return True
        next_index = self._step + 1
        self._apply_step_layout()
        self._animator.transition_to(
            self._stack.widget(next_index),
            forward=True,
            full_slide=True,
        )
        self._step = next_index
        return True

    def go_back(self) -> bool:
        if self._step <= 0:
            return False
        prev_index = self._step - 1
        self._apply_step_layout()
        self._animator.transition_to(
            self._stack.widget(prev_index),
            forward=False,
            full_slide=True,
        )
        self._step = prev_index
        return True

    def validate_step(self, step: int) -> str | None:
        if step == 1:
            if not self.object_name_edit.text().strip() and not self.title_edit.text().strip():
                return "Bitte mindestens Projektname oder Objektbezeichnung eingeben."
        return None

    def validate(self) -> str | None:
        for step in range(self.STEP_COUNT):
            error = self.validate_step(step)
            if error:
                return error
        return None

    def apply_client_profile(self, profile: ClientProfile) -> None:
        self.client_name_edit.setText(profile.name)
        self.client_address_edit.setText(profile.address)
        self.client_email_edit.setText(profile.email)
        self.client_phone_edit.setText(profile.phone)
        self.client_name_edit.setFocus()

    def load_auftrag(self, auftrag: Auftrag) -> None:
        self.title_edit.setText(auftrag.title)
        self.client_name_edit.setText(auftrag.client_name)
        self.client_address_edit.setText(auftrag.client_address)
        self.client_email_edit.setText(auftrag.client_email)
        self.client_phone_edit.setText(auftrag.client_phone)
        self.object_name_edit.setText(auftrag.object_name)
        self.object_address_edit.setText(auftrag.object_address)
        self.editor_edit.setText(auftrag.editor)
        self.notes_edit.setPlainText(auftrag.notes)
        self.reset_steps()

    def clear_form(self) -> None:
        self.load_auftrag(Auftrag())

    def build_auftrag(self, base: Auftrag | None = None) -> Auftrag:
        auftrag = base or Auftrag()
        auftrag.title = self.title_edit.text().strip()
        auftrag.client_name = self.client_name_edit.text().strip()
        auftrag.client_address = self.client_address_edit.text().strip()
        auftrag.client_email = self.client_email_edit.text().strip()
        auftrag.client_phone = self.client_phone_edit.text().strip()
        auftrag.object_name = self.object_name_edit.text().strip()
        auftrag.object_address = self.object_address_edit.text().strip()
        auftrag.editor = self.editor_edit.text().strip()
        auftrag.notes = self.notes_edit.toPlainText().strip()
        return auftrag

    def focus_current_step(self) -> None:
        if self._step == 0:
            self.title_edit.setFocus()
        elif self._step == 1:
            self.object_name_edit.setFocus()
        else:
            self.editor_edit.setFocus()
