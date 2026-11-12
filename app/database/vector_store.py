"""Vector store operations for dense similarity retrieval."""

import math
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.database.models import StoryChunk
from app.core.logging import logger


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    """Vector repository providing similarity search for story chunks."""

    @staticmethod
    def save_chunks(db: Session, chunks: List[StoryChunk]) -> None:
        """Persists chunks with their precomputed embeddings."""
        db.add_all(chunks)
        db.commit()

    @staticmethod
    def search_similar(
        db: Session,
        story_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        chapter_filter: Optional[int] = None,
    ) -> List[Tuple[StoryChunk, float]]:
        """
        Executes similarity search over all story chunks.
        Returns ordered pairs of (StoryChunk, similarity_score).
        """
        query = db.query(StoryChunk).filter(StoryChunk.story_id == story_id)
        candidates = query.all()

        scored: List[Tuple[StoryChunk, float]] = []
        for chunk in candidates:
            if not chunk.embedding_json:
                continue
            sim = _cosine_similarity(query_embedding, chunk.embedding_json)
            scored.append((chunk, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

