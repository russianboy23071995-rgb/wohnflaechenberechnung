"""Tests für Vorbemerkungen."""

from wohnflaechen.application.services.preface_service import (
    build_default_preface,
    default_preface_text,
    preface_block_type,
)
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.presentation.pdf.formatters import preface_content_html


def test_build_default_preface_on_site():
    from datetime import date

    project = Project(measurement_on_site=True, measurement_date=date(2026, 5, 9))
    text = build_default_preface(project)
    assert "1. Grundlagen der Ermittlung" in text
    assert "2. Methodik des Aufmaßes" in text
    assert "3. Stichtag der Aufnahme" in text
    assert "4. Messgenauigkeit und Toleranzen" in text
    assert "5. Zweck und Geltungsbereich" in text
    assert "6. Hinweis zur Berechnungsgrundlage" in text
    assert "hybriden Aufmaßverfahrens" in text
    assert "Aufmaß erfolgt am: 09.05.2026" in text
    assert "Plan- und Bauunterlagen" not in text


def test_build_default_preface_from_plans():
    project = Project(measurement_on_site=False)
    text = build_default_preface(project)
    assert "2. Berechnungsgrundlage" in text
    assert "3. Grundlage der Flächenermittlung" in text
    assert "4. Berechnungsgenauigkeit und Rundung" in text
    assert "Plan- und Bauunterlagen" in text
    assert "Methodik des Aufmaßes" not in text


def test_preface_block_type_maps_variant():
    assert preface_block_type(True) is TextBlockType.PREFACE_ON_SITE
    assert preface_block_type(False) is TextBlockType.PREFACE_FROM_PLANS


def test_default_texts_are_independent():
    on_site = default_preface_text(True)
    from_plans = default_preface_text(False)
    assert on_site != from_plans
    assert "LiDAR" in on_site
    assert "Auftraggebers wurde bestätigt" in from_plans


def test_preface_html_keeps_bold_titles():
    html = str(preface_content_html(default_preface_text(True)))
    assert "<strong>1. Grundlagen der Ermittlung</strong>" in html
    assert "<strong>2. Methodik des Aufmaßes</strong>" in html
    assert "Bachelor of Architecture" in html


def test_apply_measurement_date_updates_only_date_line():
    from datetime import date

    from wohnflaechen.application.services.preface_service import apply_measurement_date

    original = default_preface_text(True, date(2026, 1, 1))
    original = original.replace("Bachelor of Architecture", "Eigener Methodiktext")
    updated = apply_measurement_date(original, date(2026, 9, 16))
    assert "Eigener Methodiktext" in updated
    assert "Aufmaß erfolgt am: 16.09.2026" in updated
    assert "01.01.2026" not in updated
