"""Corporate UI-Theme – NOVIKOV Produkt-Look (angelehnt an Website-Vorlagen)."""

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

COLOR_BG = "#f3f3f3"
COLOR_SURFACE = "#ffffff"
COLOR_TEXT = "#1c1c1c"
COLOR_TEXT_MUTED = "#6e6e6e"
COLOR_PRIMARY = "#2e2e2e"
COLOR_PRIMARY_HOVER = "#404040"
COLOR_BORDER = "#e6e6e6"
COLOR_BEIGE = "#ebe6dc"
COLOR_BADGE_DONE = "#e8f5e9"
COLOR_BADGE_PENDING = "#f5f5f5"

APP_STYLESHEET = """
QMainWindow, QDialog, QWizard {
    background: #f3f3f3;
}

QWidget#appBackground {
    background-color: #f3f3f3;
}

QWidget#heroCard, QWidget#glassPanel, QWidget#welcomeCard, QWidget#hubCard {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 20px;
}

QWidget#entryCard {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 16px;
}

QFrame#entryCard {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 16px;
}

QFrame#inlinePanel {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 16px;
}

QFrame#entryCardCompact {
    background-color: #fafafa;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
}

QWidget#dashboardMain {
    background-color: transparent;
}

QScrollArea#inlinePanelScroll {
    background-color: transparent;
    border: none;
}

QTreeWidget#folderTree {
    background-color: transparent;
    border: none;
}

QFrame#sidePanel {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 16px;
}

QFrame#resizeGrip {
    background-color: transparent;
    border: none;
    margin: 8px 0;
}

QFrame#resizeGrip:hover {
    background-color: #e0e0e0;
    border-radius: 4px;
}

QPushButton#profileCardButton {
    background-color: #fafafa;
    border: 1px solid #ececec;
    border-radius: 12px;
    padding: 10px 14px;
    text-align: left;
    color: #1c1c1c;
}

QPushButton#profileCardButton:hover {
    background-color: #f0f0f0;
    border-color: #d8d8d8;
}

QPushButton#profileCardButton:pressed {
    background-color: #e8e8e8;
}

QFrame#formGroup {
    background-color: #fafafa;
    border: 1px solid #ececec;
    border-radius: 14px;
}

QLabel#formGroupTitle {
    font-size: 11pt;
    font-weight: 600;
    color: #1c1c1c;
}

QLabel#brandTitle {
    font-size: 20px;
    font-weight: 600;
    color: #1c1c1c;
}

QLabel#brandSubtitle {
    font-size: 10pt;
    color: #6e6e6e;
}

QLabel#heroHeadline {
    font-size: 15pt;
    font-weight: 600;
    color: #1c1c1c;
    margin-top: 8px;
}

QLabel#sectionTitle {
    font-size: 12pt;
    font-weight: 700;
    color: #1c1c1c;
}

QLabel#entryTitle {
    font-size: 11pt;
    font-weight: 600;
    color: #1c1c1c;
}

QLabel#entryMeta {
    font-size: 9pt;
    color: #6e6e6e;
}

QLabel#statusBadgeDone {
    background-color: #eef6ee;
    color: #2d5a2d;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 8.5pt;
}

QLabel#statusBadgePending {
    background-color: #f0f0f0;
    color: #888888;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 8.5pt;
}

QLabel#headerTitle {
    font-size: 14pt;
    font-weight: 600;
    color: #1c1c1c;
    padding: 4px 8px;
}

QLabel#hintText {
    color: #6e6e6e;
    font-size: 9pt;
}

QLabel#warningText {
    color: #9a6700;
    font-size: 9pt;
}

QLabel#metricValue {
    font-weight: 700;
    color: #1c1c1c;
}

QScrollArea#dashboardScroll {
    background: transparent;
}

QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e8e8e8;
    padding: 4px 12px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 8px;
}

QMenuBar::item:selected {
    background-color: #f0f0f0;
}

QToolBar#homeNavBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e8e8e8;
    spacing: 6px;
    padding: 4px 10px;
}

QToolBar#homeNavBar QToolButton {
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 6px;
}

QToolBar#homeNavBar QToolButton:hover {
    background-color: #f0f0f0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #f3f3f3;
}

QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e8e8e8;
    color: #6e6e6e;
}

QPushButton {
    background-color: #ffffff;
    color: #1c1c1c;
    border: 1px solid #dcdcdc;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #fafafa;
    border-color: #c8c8c8;
}

QPushButton#primaryButton {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #2e2e2e;
    font-weight: 600;
    border-radius: 12px;
}

QPushButton#primaryButton:hover {
    background-color: #404040;
}

QPushButton#primaryButton:pressed {
    background-color: #1a1a1a;
}

QPushButton#secondaryButton {
    background-color: #ffffff;
    color: #1c1c1c;
    border: 1px solid #d0d0d0;
    font-weight: 500;
    border-radius: 12px;
}

QPushButton#secondaryButton:hover {
    background-color: #f7f7f7;
}

QPushButton#ghostButton {
    background-color: transparent;
    border: 1px solid #e0e0e0;
    color: #1c1c1c;
    border-radius: 10px;
    padding: 6px 12px;
}

QPushButton#ghostButton:hover {
    background-color: #f5f5f5;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDateEdit {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    padding: 8px 10px;
    color: #1c1c1c;
    min-height: 22px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDateEdit:focus {
    border: 1px solid #b0b0b0;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    padding: 6px 10px;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #fafafa;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    gridline-color: #f0f0f0;
    selection-background-color: #ebe6dc;
    selection-color: #1c1c1c;
}

QHeaderView::section {
    background-color: #fafafa;
    color: #4a4a4a;
    border: none;
    border-bottom: 1px solid #e8e8e8;
    padding: 8px 6px;
    font-weight: 600;
    font-size: 9pt;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    padding: 6px;
}

QListWidget::item:selected {
    background-color: #ebe6dc;
    color: #1c1c1c;
}

QSplitter::handle {
    background-color: transparent;
    width: 10px;
}

QWizard, QDialog {
    background-color: #f3f3f3;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #d0d0d0;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #2e2e2e;
    border-color: #2e2e2e;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px;
}

QScrollBar::handle:vertical {
    background: #d0d0d0;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background: #d0d0d0;
    border-radius: 5px;
}
"""


def apply_app_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLOR_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLOR_TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLOR_SURFACE))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLOR_TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLOR_SURFACE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLOR_TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLOR_PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet(APP_STYLESHEET)
