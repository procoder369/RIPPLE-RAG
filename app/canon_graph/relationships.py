"""Relationship definitions between story entities."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RelationType(str, Enum):
    ALLIED_WITH = "ALLIED_WITH"
    ENEMY_OF = "ENEMY_OF"
    PARENT_OF = "PARENT_OF"
    CHILD_OF = "CHILD_OF"
    SIBLING_OF = "SIBLING_OF"
    MARRIED_TO = "MARRIED_TO"
    LOCATED_IN = "LOCATED_IN"
    OWNS = "OWNS"
    KILLED = "KILLED"
    MEMBER_OF = "MEMBER_OF"
    WIELDS = "WIELDS"


class RelationshipDTO(BaseModel):
    """Represents a directional relationship between two entities."""
    id: Optional[str] = None
    story_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    valid_from_chapter: int = 1
    valid_to_chapter: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

