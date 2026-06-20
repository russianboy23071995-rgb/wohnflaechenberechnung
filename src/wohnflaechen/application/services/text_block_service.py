"""Objekttext-Verwaltung."""

from wohnflaechen.domain.entities.text_block import TextBlock
from wohnflaechen.domain.enums.text_block_type import TextBlockType
from wohnflaechen.domain.repositories.interfaces import TextBlockRepository


class TextBlockService:
    """Use Cases für Objektinformationen."""

    def __init__(self, text_block_repository: TextBlockRepository) -> None:
        self._text_blocks = text_block_repository

    def list_text_blocks(self, project_id: int) -> list[TextBlock]:
        return self._text_blocks.list_by_project(project_id)

    def get_text_block(
        self, project_id: int, block_type: TextBlockType
    ) -> TextBlock:
        existing = self._text_blocks.get_by_type(project_id, block_type)
        if existing:
            return existing
        return TextBlock(project_id=project_id, block_type=block_type, content="")

    def save_text_block(self, text_block: TextBlock) -> TextBlock:
        return self._text_blocks.save(text_block)
