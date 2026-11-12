"""Sparse lexical keyword retrieval using BM25 for fiction terms."""

import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.database.models import StoryChunk

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False


def _tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric tokens."""
    return re.findall(r"\w+", text.lower())


class SparseRetriever:
    """Performs BM25 keyword matching across story chunks."""

    @staticmethod
    def retrieve(
        db: Session,
        story_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[StoryChunk, float]]:
        """Searches story chunks using BM25 token matching."""
        chunks = db.query(StoryChunk).filter(StoryChunk.story_id == story_id).all()
        if not chunks:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        if HAS_BM25:
            corpus = [_tokenize(c.content) for c in chunks]
            bm25 = BM25Okapi(corpus)
            doc_scores = bm25.get_scores(query_tokens)
            ranked_pairs = list(zip(chunks, doc_scores))
            ranked_pairs.sort(key=lambda x: x[1], reverse=True)
            return ranked_pairs[:top_k]

        # Basic fallback term-frequency scoring if rank_bm25 is not installed
        scored: List[Tuple[StoryChunk, float]] = []
        for c in chunks:
            text_lower = c.content.lower()
            score = sum(text_lower.count(token) for token in query_tokens)
            if score > 0:
                scored.append((c, float(score)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

