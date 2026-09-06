"""Ordnernavigation – Kunden, Objekte, Angebote, Rechnungen."""

from wohnflaechen.domain.entities.folder import Folder
from wohnflaechen.infrastructure.database.folder_repository import SQLiteFolderRepository


class FolderService:
    CATEGORIES = ("vorgaenge", "kunden", "objekte", "angebote", "rechnungen")

    def __init__(self, repository: SQLiteFolderRepository) -> None:
        self._folders = repository

    def list_folders(self) -> list[Folder]:
        return self._folders.list_all()

    def get_folder(self, folder_id: int) -> Folder | None:
        return self._folders.get_by_id(folder_id)

    def create_subfolder(self, parent_id: int, name: str) -> Folder:
        parent = self._folders.get_by_id(parent_id)
        if parent is None:
            raise ValueError("Überordner nicht gefunden.")
        siblings = [f for f in self._folders.list_all() if f.parent_id == parent_id]
        folder = Folder(
            name=name.strip(),
            parent_id=parent_id,
            category=parent.category,
            sort_order=len(siblings),
        )
        return self._folders.save(folder)

    def move_item(self, folder_id: int, entity_type: str, entity_id: int) -> None:
        self._folders.move_item(folder_id, entity_type, entity_id)

    def list_folder_items(self, folder_id: int) -> list[tuple[str, int]]:
        return self._folders.list_items(folder_id)

    def folder_item_keys(self, folder_id: int) -> set[str]:
        keys: set[str] = set()
        for entity_type, entity_id in self._folders.list_items(folder_id):
            if entity_type == "auftrag":
                keys.add(f"auftrag-{entity_id}")
            elif entity_type == "project":
                keys.add(f"project-{entity_id}")
        return keys
