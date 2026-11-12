"""Reranker for scoring and ordering evidence chunks."""

from typing import List, Tuple
from app.database.models import StoryChunk


class Reranker:
    """Reranks retrieved story chunks using query-passage alignment."""

    @staticmethod
    def rerank(
        query: str,
        scored_chunks: List[Tuple[StoryChunk, float]],
        top_n: int = 5,
    ) -> List[Tuple[StoryChunk, float]]:
        """Reranks candidate chunks by incorporating token overlap and dialogue presence."""
        query_terms = set(query.lower().split())
        reranked: List[Tuple[StoryChunk, float]] = []

        for chunk, base_score in scored_chunks:
            content_lower = chunk.content.lower()
            # Boost score if dialogue quotes are present
            dialogue_boost = 1.15 if '"' in chunk.content else 1.0
            # Term coverage ratio
            coverage = sum(1 for term in query_terms if term in content_lower) / max(len(query_terms), 1)
            final_score = (base_score * 0.7 + coverage * 0.3) * dialogue_boost
            reranked.append((chunk, final_score))

        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_n]

