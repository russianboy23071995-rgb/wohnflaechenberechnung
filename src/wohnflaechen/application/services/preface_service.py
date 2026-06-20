"""Vorbemerkungen – Textaufbau und Synchronisation."""

import re

from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.preface.preface_templates import (
    DEFAULT_PREFACE_SECTIONS,
    section_3_body,
)

_SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+")


def _format_section(title: str, body: str) -> str:
    return f"{title}\n{body.strip()}"


def _parse_preface(text: str) -> list[tuple[str, str]]:
    if not text.strip():
        return []

    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    body_lines: list[str] = []

    for line in text.splitlines():
        if _SECTION_HEADER_PATTERN.match(line.strip()):
            if current_title is not None:
                sections.append((current_title, "\n".join(body_lines).strip()))
            current_title = line.strip()
            body_lines = []
        else:
            body_lines.append(line)

    if current_title is not None:
        sections.append((current_title, "\n".join(body_lines).strip()))

    return sections


def build_default_preface(project: Project) -> str:
    """Erzeugt die vollständigen Vorbemerkungen mit Standardtexten."""
    parts: list[str] = []
    for section in DEFAULT_PREFACE_SECTIONS:
        if section.number == 3:
            body = section_3_body(project.measurement_on_site, project.measurement_date)
        else:
            body = section.default_body
        parts.append(_format_section(section.title, body))
    return "\n\n".join(parts)


def sync_preface_with_project(project: Project, existing_preface: str) -> str:
    """Aktualisiert Punkt 3; andere Abschnitte bleiben erhalten."""
    parsed = _parse_preface(existing_preface)
    new_section_3 = section_3_body(project.measurement_on_site, project.measurement_date)

    if len(parsed) < 3:
        return build_default_preface(project)

    updated: list[str] = []
    for index, (title, body) in enumerate(parsed, start=1):
        if index == 3:
            body = new_section_3
        updated.append(_format_section(title, body))
    return "\n\n".join(updated)
