"""Dense vector retrieval using embeddings and cosine similarity."""

from typing import List, Tuple
from sqlalchemy.orm import Session
from app.database.models import StoryChunk
from app.database.vector_store import VectorStore
from app.ingestion.embedder import Embedder


class DenseRetriever:
    """Performs semantic similarity search over story chunk embeddings."""

    def __init__(self, embedder: Embedder = None):
        self.embedder = embedder or Embedder()

    def retrieve(
        self,
        db: Session,
        story_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[StoryChunk, float]]:
        """Embeds query and queries the vector store."""
        query_embedding = self.embedder.embed_text(query)
        return VectorStore.search_similar(
            db=db,
            story_id=story_id,
            query_embedding=query_embedding,
            top_k=top_k,
        )

