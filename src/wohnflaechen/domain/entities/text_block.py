"""Objekttext-Entität."""

from dataclasses import dataclass
from typing import Optional

from wohnflaechen.domain.enums.text_block_type import TextBlockType


@dataclass
class TextBlock:
    """Freitext-Block für Objektinformationen."""

    id: Optional[int] = None
    project_id: int = 0
    block_type: TextBlockType = TextBlockType.OBJECT_DESCRIPTION
    content: str = ""
