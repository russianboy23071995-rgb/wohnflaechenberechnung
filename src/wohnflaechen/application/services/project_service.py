"""Projektverwaltung."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from wohnflaechen.application.services.preface_service import (
    apply_measurement_date,
    default_preface_text,
    preface_block_type,
)
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.domain.repositories.interfaces import (
    ProjectRepository,
    TextBlockRepository,
)
from wohnflaechen.infrastructure.database.connection import DatabaseConnection
from wohnflaechen.infrastructure.database.schema import initialize_schema


class ProjectService:
    """Use Cases für Projektanlage, -speicherung und -liste."""

    def __init__(
        self,
        connection: DatabaseConnection,
        project_repository: ProjectRepository,
        text_block_repository: TextBlockRepository,
    ) -> None:
        self._connection = connection
        self._projects = project_repository
        self._text_blocks = text_block_repository

    def initialize_database(self) -> None:
        initialize_schema(self._connection)

    def list_projects(self) -> list[Project]:
        return self._projects.list_all()

    def list_projects_for_auftrag(self, auftrag_id: int) -> list[Project]:
        return self._projects.list_by_auftrag(auftrag_id)

    def get_project(self, project_id: int) -> Optional[Project]:
        return self._projects.get_by_id(project_id)

    def create_project(self, project: Project, file_path: Optional[Path] = None) -> Project:
        project.created_at = datetime.now()
        if file_path:
            project.file_path = str(file_path)
        saved = self._projects.save(project)
        self._ensure_default_text_blocks(saved)
        return saved

    def save_project(self, project: Project) -> Project:
        saved = self._projects.save(project)
        self._fill_preface_if_empty(saved)
        self._sync_measurement_date(saved)
        return saved

    def set_project_completed(self, project_id: int, completed: bool) -> Project | None:
        project = self._projects.get_by_id(project_id)
        if project is None:
            return None
        project.completed = completed
        return self._projects.save(project)

    def ensure_preface(self, project_id: int) -> None:
        """Füllt leere Vorbemerkungen mit Standardtexten, ohne bestehende Texte zu überschreiben."""
        project = self.get_project(project_id)
        if project:
            self._fill_preface_if_empty(project)
            self._sync_measurement_date(project)

    def delete_project(self, project_id: int) -> None:
        self._projects.delete(project_id)

    def _ensure_default_text_blocks(self, project: Project) -> None:
        project_id = project.id
        if project_id is None:
            return

        for block_type in TextBlockType:
            existing = self._text_blocks.get_by_type(project_id, block_type)
            if existing is None:
                self._text_blocks.save(
                    TextBlock(project_id=project_id, block_type=block_type, content="")
                )

        self._fill_preface_if_empty(project)

    def _fill_preface_if_empty(self, project: Project) -> None:
        if project.id is None:
            return

        legacy = self._text_blocks.get_by_type(project.id, TextBlockType.PREFACE)
        legacy_text = legacy.content.strip() if legacy else ""

        for on_site in (True, False):
            block_type = preface_block_type(on_site)
            block = self._text_blocks.get_by_type(project.id, block_type)
            if block is None:
                block = TextBlock(project_id=project.id, block_type=block_type)
            if block.content.strip():
                continue
            if legacy_text and on_site == project.measurement_on_site:
                block.content = legacy.content
            else:
                block.content = default_preface_text(on_site, project.measurement_date)
            self._text_blocks.save(block)

        self._sync_active_preface(project)

    def _sync_measurement_date(self, project: Project) -> None:
        if project.id is None:
            return
        block = self._text_blocks.get_by_type(project.id, TextBlockType.PREFACE_ON_SITE)
        if block is None or not block.content.strip():
            return
        updated = apply_measurement_date(block.content, project.measurement_date)
        if updated != block.content:
            block.content = updated
            self._text_blocks.save(block)
        self._sync_active_preface(project)

    def _sync_active_preface(self, project: Project) -> None:
        if project.id is None:
            return
        active_type = preface_block_type(project.measurement_on_site)
        active = self._text_blocks.get_by_type(project.id, active_type)
        if active is None or not active.content.strip():
            return
        mirror = self._text_blocks.get_by_type(project.id, TextBlockType.PREFACE)
        if mirror is None:
            mirror = TextBlock(project_id=project.id, block_type=TextBlockType.PREFACE)
        mirror.content = active.content
        self._text_blocks.save(mirror)
