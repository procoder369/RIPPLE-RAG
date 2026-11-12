"""Entity definitions and attributes for CanonGraph."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    FACTION = "faction"
    CONCEPT = "concept"


class EntityDTO(BaseModel):
    """Data transfer object for story canon entities."""
    id: Optional[str] = None
    story_id: str
    name: str
    entity_type: EntityType
    aliases: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    first_seen_chapter: Optional[int] = None

