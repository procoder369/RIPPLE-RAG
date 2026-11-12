"""SQLAlchemy models for stories, chunks, embeddings, canon entities, and facts."""

import datetime
import uuid
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SqlEnum,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Story(Base):
    """Represents a story universe or manuscript."""
    __tablename__ = "stories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    author_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    chapters = relationship("Chapter", back_populates="story", cascade="all, delete-orphan")
    entities = relationship("CanonEntity", back_populates="story", cascade="all, delete-orphan")
    facts = relationship("CanonFact", back_populates="story", cascade="all, delete-orphan")


class Chapter(Base):
    """A chapter, episode, or scene manuscript belonging to a story."""
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    chapter_index = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    story = relationship("Story", back_populates="chapters")
    chunks = relationship("StoryChunk", back_populates="chapter", cascade="all, delete-orphan")


class StoryChunk(Base):
    """Scene-aware chunk extracted from a chapter for vector search."""
    __tablename__ = "story_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    scene_number = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    # Stored as JSON list of floats for broad database compatibility (SQLite / Postgres)
    embedding_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    chapter = relationship("Chapter", back_populates="chunks")


class CanonEntity(Base):
    """Entity in the story world (character, location, item, faction)."""
    __tablename__ = "canon_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)  # character, location, item, concept
    aliases = Column(JSON, default=list)  # alternate names/nicknames
    attributes = Column(JSON, default=dict)  # current state / traits
    first_seen_chapter = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    story = relationship("Story", back_populates="entities")
    facts = relationship("CanonFact", back_populates="entity", cascade="all, delete-orphan")


class CanonFact(Base):
    """Grounded fact asserted about an entity or timeline event."""
    __tablename__ = "canon_facts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    entity_id = Column(String(36), ForeignKey("canon_entities.id"), nullable=True)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), nullable=True)
    statement = Column(Text, nullable=False)
    category = Column(String(50), default="general")  # state, relationship, event, trait
    timeline_order = Column(Integer, default=0)
    status = Column(String(30), default="PROPOSED")  # PROPOSED, APPROVED, REJECTED, SUPERSEDED
    confidence = Column(Float, default=1.0)
    source_quote = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    story = relationship("Story", back_populates="facts")
    entity = relationship("CanonEntity", back_populates="facts")


class CanonRelationship(Base):
    """Directed connection between two canon entities."""
    __tablename__ = "canon_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    source_entity_id = Column(String(36), ForeignKey("canon_entities.id"), nullable=False)
    target_entity_id = Column(String(36), ForeignKey("canon_entities.id"), nullable=False)
    relation_type = Column(String(100), nullable=False)  # e.g., "ALLIED_WITH", "OWNS", "LOCATED_IN"
    valid_from_chapter = Column(Integer, default=1)
    valid_to_chapter = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict)


class ContinuityViolation(Base):
    """Record of identified narrative contradictions or timeline conflicts."""
    __tablename__ = "continuity_violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String(36), ForeignKey("stories.id"), nullable=False)
    chapter_id = Column(String(36), nullable=True)
    violation_type = Column(String(100), nullable=False)  # e.g., "TEMPORAL_PARADOX", "STATE_CONTRADICTION"
    severity = Column(String(30), default="WARNING")  # INFO, WARNING, BLOCKING
    description = Column(Text, nullable=False)
    conflicting_fact_ids = Column(JSON, default=list)
    suggested_fix = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

