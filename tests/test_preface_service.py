"""Tests für Vorbemerkungen."""

from datetime import date

from wohnflaechen.application.services.preface_service import (
    build_default_preface,
    sync_preface_with_project,
)
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.preface.preface_templates import SECTION_3_BODY_NO_MEASUREMENT


def test_build_default_preface_contains_all_sections():
    project = Project(measurement_on_site=True, measurement_date=date(2026, 5, 9))
    text = build_default_preface(project)
    assert "1. Grundlagen der Ermittlung" in text
    assert "2. Methodik des Aufmaßes" in text
    assert "3. Stichtag der Aufnahme" in text
    assert "4. Messgenauigkeit und Toleranzen" in text
    assert "5. Zweck und Geltungsbereich" in text
    assert "6. Haftungshinweis" in text
    assert "09.05.2026" in text


def test_section_3_without_measurement():
    project = Project(measurement_on_site=False)
    text = build_default_preface(project)
    assert SECTION_3_BODY_NO_MEASUREMENT in text


def test_sync_updates_only_section_3():
    project = Project(measurement_on_site=True, measurement_date=date(2026, 6, 20))
    original = build_default_preface(Project(measurement_on_site=False))
    original = original.replace(
        SECTION_3_BODY_NO_MEASUREMENT,
        "Alter Text Punkt 3",
    )
    synced = sync_preface_with_project(project, original)
    assert "20.06.2026" in synced
    assert "1. Grundlagen der Ermittlung" in synced
    assert SECTION_3_BODY_NO_MEASUREMENT not in synced
