"""Indexes processed chunks and extracted facts into database and vector store."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import StoryChunk, CanonEntity, CanonFact
from app.database.vector_store import VectorStore
from app.canon_graph.fact_store import FactStore
from app.core.logging import logger


class Indexer:
    """Orchestrates writing chunk embeddings and initial proposed facts into storage."""

    @staticmethod
    def index_chapter_chunks(
        db: Session,
        story_id: str,
        chapter_id: str,
        chunks_data: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> List[StoryChunk]:
        """Saves chunks with embeddings into the database."""
        chunk_models: List[StoryChunk] = []

        for idx, (data, emb) in enumerate(zip(chunks_data, embeddings)):
            chunk = StoryChunk(
                story_id=story_id,
                chapter_id=chapter_id,
                chunk_index=data.get("chunk_index", idx),
                scene_number=data.get("scene_number", 1),
                content=data["content"],
                token_count=data.get("word_count", len(data["content"].split())),
                embedding_json=emb,
                metadata_json={"scene": data.get("scene_number", 1)},
            )
            chunk_models.append(chunk)

        VectorStore.save_chunks(db, chunk_models)
        logger.info(f"Indexed {len(chunk_models)} chunks for chapter {chapter_id}")
        return chunk_models

    @staticmethod
    def index_extracted_facts(
        db: Session,
        story_id: str,
        chapter_id: str,
        timeline_order: int,
        extracted_facts: List[Dict[str, Any]],
    ) -> List[CanonFact]:
        """Stores extracted facts and links or creates candidate entities."""
        saved_facts: List[CanonFact] = []

        for fact_dict in extracted_facts:
            entity_name = fact_dict.get("entity_name")
            entity_id = None

            if entity_name:
                # Find or create candidate entity
                entity = (
                    db.query(CanonEntity)
                    .filter(
                        CanonEntity.story_id == story_id,
                        CanonEntity.name == entity_name,
                    )
                    .first()
                )
                if not entity:
                    entity = CanonEntity(
                        story_id=story_id,
                        name=entity_name,
                        entity_type="character",
                        first_seen_chapter=timeline_order,
                    )
                    db.add(entity)
                    db.commit()
                    db.refresh(entity)
                entity_id = entity.id

            fact = FactStore.propose_fact(
                db=db,
                story_id=story_id,
                statement=fact_dict["statement"],
                entity_id=entity_id,
                chapter_id=chapter_id,
                timeline_order=timeline_order,
                source_quote=fact_dict.get("source_quote"),
                category=fact_dict.get("category", "general"),
            )
            saved_facts.append(fact)

        return saved_facts

