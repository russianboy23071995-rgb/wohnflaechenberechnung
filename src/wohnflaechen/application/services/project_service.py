"""Projektverwaltung."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from wohnflaechen.application.services.preface_service import (
    build_default_preface,
    sync_preface_with_project,
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
        self._sync_preface(saved)
        return saved

    def ensure_preface(self, project_id: int) -> None:
        """Füllt leere Vorbemerkungen mit Standardtexten."""
        project = self.get_project(project_id)
        if project:
            self._sync_preface(project)

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

        preface = self._text_blocks.get_by_type(project_id, TextBlockType.PREFACE)
        if preface and not preface.content.strip():
            preface.content = build_default_preface(project)
            self._text_blocks.save(preface)

    def _sync_preface(self, project: Project) -> None:
        if project.id is None:
            return

        preface = self._text_blocks.get_by_type(project.id, TextBlockType.PREFACE)
        if preface is None:
            preface = TextBlock(project_id=project.id, block_type=TextBlockType.PREFACE)

        if not preface.content.strip():
            preface.content = build_default_preface(project)
        else:
            preface.content = sync_preface_with_project(project, preface.content)

        self._text_blocks.save(preface)
