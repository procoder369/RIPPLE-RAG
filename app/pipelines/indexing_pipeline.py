"""Pipeline A: Ingestion, scene-aware chunking, embedding, and fact extraction."""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Chapter, Story
from app.ingestion.loader import DocumentLoader
from app.ingestion.preprocessor import TextPreprocessor
from app.ingestion.chunker import SceneAwareChunker
from app.ingestion.embedder import Embedder
from app.ingestion.fact_extractor import FactExtractor
from app.ingestion.indexer import Indexer
from app.core.logging import logger


class IndexingPipeline:
    """Orchestrates Pipeline A (Chapter ingestion to indexed vector & canon knowledge)."""

    def __init__(self, embedder: Embedder = None, chunker: SceneAwareChunker = None):
        self.chunker = chunker or SceneAwareChunker()
        self.embedder = embedder or Embedder()
        self.fact_extractor = FactExtractor()

    def run(
        self,
        db: Session,
        story_id: str,
        chapter_title: str,
        chapter_index: int,
        raw_text: str,
    ) -> Dict[str, Any]:
        """Executes end-to-end ingestion and indexing pipeline for a manuscript chapter."""
        logger.info(f"Starting Indexing Pipeline for story {story_id}, chapter {chapter_index}: {chapter_title}")

        # 1. Ensure story exists
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            story = Story(id=story_id, title="Untitled Story")
            db.add(story)
            db.commit()

        # 2. Document Loading & Preprocessing
        doc_data = DocumentLoader.load_from_text(raw_text, chapter_title, chapter_index)
        cleaned_text = TextPreprocessor.clean_text(doc_data["raw_text"])

        # 3. Create or update Chapter record
        chapter = (
            db.query(Chapter)
            .filter(Chapter.story_id == story_id, Chapter.chapter_index == chapter_index)
            .first()
        )
        if not chapter:
            chapter = Chapter(
                story_id=story_id,
                chapter_index=chapter_index,
                title=chapter_title,
                raw_text=cleaned_text,
                word_count=len(cleaned_text.split()),
            )
            db.add(chapter)
            db.commit()
            db.refresh(chapter)

        # 4. Scene-aware chunking
        chunks_data = self.chunker.process(cleaned_text)
        logger.info(f"Generated {len(chunks_data)} scene-aware chunks.")

        # 5. Embeddings generation
        chunk_texts = [c["content"] for c in chunks_data]
        embeddings = self.embedder.embed_batch(chunk_texts)

        # 6. Index chunks into vector store
        indexed_chunks = Indexer.index_chapter_chunks(
            db=db,
            story_id=story_id,
            chapter_id=chapter.id,
            chunks_data=chunks_data,
            embeddings=embeddings,
        )

        # 7. Extract and index proposed facts
        all_extracted_facts = []
        for chunk in chunks_data:
            extracted = self.fact_extractor.extract_from_chunk(chunk["content"], chapter_index)
            all_extracted_facts.extend(extracted)

        saved_facts = Indexer.index_extracted_facts(
            db=db,
            story_id=story_id,
            chapter_id=chapter.id,
            timeline_order=chapter_index,
            extracted_facts=all_extracted_facts,
        )

        return {
            "status": "SUCCESS",
            "story_id": story_id,
            "chapter_id": chapter.id,
            "chapter_index": chapter_index,
            "chunks_indexed": len(indexed_chunks),
            "facts_proposed": len(saved_facts),
        }

