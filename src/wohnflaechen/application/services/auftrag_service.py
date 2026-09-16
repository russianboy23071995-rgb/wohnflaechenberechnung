"""Auftragsverwaltung."""

from datetime import datetime
from typing import Optional

from wohnflaechen.domain.entities.auftrag import Auftrag
from wohnflaechen.domain.entities.project import Project
from wohnflaechen.infrastructure.database.auftrag_repositories import SQLiteAuftragRepository
from wohnflaechen.domain.repositories.interfaces import ProjectRepository


class AuftragService:
    def __init__(
        self,
        auftrag_repository: SQLiteAuftragRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._auftraege = auftrag_repository
        self._projects = project_repository

    def list_auftraege(self) -> list[Auftrag]:
        return self._auftraege.list_all()

    def get_auftrag(self, auftrag_id: int) -> Optional[Auftrag]:
        return self._auftraege.get_by_id(auftrag_id)

    def create_auftrag(self, auftrag: Auftrag) -> Auftrag:
        auftrag.created_at = datetime.now()
        return self._auftraege.save(auftrag)

    def save_auftrag(self, auftrag: Auftrag) -> Auftrag:
        return self._auftraege.save(auftrag)

    def set_auftrag_completed(self, auftrag_id: int, completed: bool) -> Auftrag | None:
        auftrag = self._auftraege.get_by_id(auftrag_id)
        if auftrag is None:
            return None
        auftrag.completed = completed
        return self._auftraege.save(auftrag)

    def delete_auftrag(self, auftrag_id: int) -> None:
        self._auftraege.delete(auftrag_id)

    def get_woflv_project(self, auftrag_id: int) -> Optional[Project]:
        projects = self._projects.list_by_auftrag(auftrag_id)
        return projects[0] if projects else None

    def project_from_auftrag(self, auftrag: Auftrag) -> Project:
        """Erzeugt ein WoFlV-Projekt mit übernommenen Stammdaten."""
        return Project(
            auftrag_id=auftrag.id,
            name=auftrag.title or auftrag.object_name,
            object_name=auftrag.object_name,
            address=auftrag.object_address,
            client=auftrag.client_name,
            editor=auftrag.editor,
        )
