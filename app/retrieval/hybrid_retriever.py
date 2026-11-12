"""Hybrid retrieval combining dense vector similarity and sparse lexical matching."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import StoryChunk
from app.retrieval.dense_retriever import DenseRetriever
from app.retrieval.sparse_retriever import SparseRetriever
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.query_processor import QueryProcessor


class HybridRetriever:
    """Fuses dense vector results and sparse lexical results via Reciprocal Rank Fusion."""

    def __init__(self, dense_retriever: DenseRetriever = None):
        self.dense = dense_retriever or DenseRetriever()
        self.sparse = SparseRetriever()
        self.graph = GraphRetriever()

    def retrieve(
        self,
        db: Session,
        story_id: str,
        query: str,
        top_k: int = 5,
        rrf_constant: int = 60,
    ) -> Dict[str, Any]:
        """
        Executes hybrid fusion retrieval and CanonGraph lookup.
        """
        processed_query = QueryProcessor.process_query(query)
        dense_results = self.dense.retrieve(db, story_id, query, top_k=top_k * 2)
        sparse_results = self.sparse.retrieve(db, story_id, query, top_k=top_k * 2)

        # Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, StoryChunk] = {}

        for rank, (chunk, _) in enumerate(dense_results, start=1):
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + (1.0 / (rrf_constant + rank))
            chunk_map[chunk.id] = chunk

        for rank, (chunk, _) in enumerate(sparse_results, start=1):
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + (1.0 / (rrf_constant + rank))
            chunk_map[chunk.id] = chunk

        # Sort chunks by fused RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        top_chunks = [(chunk_map[cid], rrf_scores[cid]) for cid in sorted_ids[:top_k]]

        # Retrieve graph facts for mentioned entities
        graph_context = self.graph.retrieve_entity_context(
            db, story_id, processed_query["entity_mentions"]
        )

        return {
            "query_analysis": processed_query,
            "text_chunks": top_chunks,
            "graph_context": graph_context,
        }

