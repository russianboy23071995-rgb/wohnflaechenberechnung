"""Corporate Design – NOVIKOV | PLAN & MAß."""

from pathlib import Path

_PACKAGE_DIR = Path(__file__).parent
_STATIC_DIR = _PACKAGE_DIR / "static"

COMPANY_NAME = "NOVIKOV | PLAN & MAß"
COMPANY_TAGLINE = "Immobilien Erfassen, Digitalisieren & Visualisieren"

# Fußzeile laut Vorlage (ASCII-Schreibweise)
FOOTER_WEBSITE = "www.novikov-plan-mass.de"
FOOTER_EMAIL = "info@novikov-plan-mass.de"

DOCUMENT_TITLE_LINE_1 = "Wohn-, und"
DOCUMENT_TITLE_LINE_2 = "Nutzflächenberechnung"
DOCUMENT_SUBTITLE = "nach (WoFlV)"
DOCUMENT_TITLE_FULL = f"{DOCUMENT_TITLE_LINE_1} {DOCUMENT_TITLE_LINE_2} {DOCUMENT_SUBTITLE}"

PREFACE_TITLE = (
    "Vorbemerkungen zur Wohn-, und Nutzflächenberechnung sowie zum Aufmaß"
)

LOGO_ICON = "logo_icon.png"
LOGO_HORIZONTAL = "logo_horizontal.png"
LOGO_FULL = "logo_full.png"
STAMP_SIGNATURE = "stamp_signature.png"
