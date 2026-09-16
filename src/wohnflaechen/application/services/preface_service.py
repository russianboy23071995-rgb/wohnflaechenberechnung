"""Vorbemerkungen – Textaufbau und Variantenwahl."""

import re
from datetime import date

from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.domain.preface.preface_templates import (
    DEFAULT_PREFACE_FROM_PLANS,
    DEFAULT_PREFACE_ON_SITE,
)

MEASUREMENT_DATE_PREFIX = "Aufmaß erfolgt am:"
_DATE_LINE_PATTERN = re.compile(rf"^{re.escape(MEASUREMENT_DATE_PREFIX)}\s*.*$", re.MULTILINE)
_SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+")


def preface_block_type(measurement_on_site: bool) -> TextBlockType:
    if measurement_on_site:
        return TextBlockType.PREFACE_ON_SITE
    return TextBlockType.PREFACE_FROM_PLANS


def format_measurement_date_line(measurement_date: date | None) -> str:
    if measurement_date is None:
        return f"{MEASUREMENT_DATE_PREFIX} "
    return f"{MEASUREMENT_DATE_PREFIX} {measurement_date.strftime('%d.%m.%Y')}"


def apply_measurement_date(text: str, measurement_date: date | None) -> str:
    """Aktualisiert nur die Datumszeile in Punkt 3, übriger Text bleibt erhalten."""
    if not text.strip():
        return text

    line = format_measurement_date_line(measurement_date)
    parsed = _parse_preface(text)
    if not parsed:
        if _DATE_LINE_PATTERN.search(text):
            return _DATE_LINE_PATTERN.sub(line, text, count=1)
        return text

    updated: list[str] = []
    for title, body in parsed:
        if title.startswith("3."):
            if _DATE_LINE_PATTERN.search(body):
                body = _DATE_LINE_PATTERN.sub(line, body, count=1)
            else:
                body = f"{body.strip()}\n\n{line}".strip()
        updated.append(f"{title}\n{body.strip()}")
    return "\n\n".join(updated)


def default_preface_text(
    measurement_on_site: bool, measurement_date: date | None = None
) -> str:
    if not measurement_on_site:
        return DEFAULT_PREFACE_FROM_PLANS
    return apply_measurement_date(DEFAULT_PREFACE_ON_SITE, measurement_date)


def build_default_preface(project: Project) -> str:
    """Erzeugt die Vorbemerkungen der zum Projekt passenden Variante."""
    return default_preface_text(project.measurement_on_site, project.measurement_date)


def _parse_preface(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    body_lines: list[str] = []

    for raw_line in text.splitlines():
        if _SECTION_HEADER_PATTERN.match(raw_line.strip()):
            if current_title is not None:
                sections.append((current_title, "\n".join(body_lines).strip()))
            current_title = raw_line.strip()
            body_lines = []
        else:
            body_lines.append(raw_line)

    if current_title is not None:
        sections.append((current_title, "\n".join(body_lines).strip()))

    return sections
