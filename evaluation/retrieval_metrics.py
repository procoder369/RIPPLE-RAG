"""Evaluation metrics for retrieval quality: Hit Rate@K and MRR."""

from typing import List, Dict, Any


def calculate_hit_rate_at_k(eval_results: List[Dict[str, Any]], k: int = 3) -> float:
    """Calculates the proportion of queries where target chapter appears in top-k citations."""
    if not eval_results:
        return 0.0
    hits = 0
    for res in eval_results:
        expected_chapter = res.get("expected_chapter")
        citations = res.get("citations", [])[:k]
        chunk_chapters = [c.get("chapter_index") for c in citations if c.get("chapter_index")]
        if expected_chapter in chunk_chapters:
            hits += 1
    return hits / len(eval_results)


def calculate_mrr(eval_results: List[Dict[str, Any]]) -> float:
    """Calculates Mean Reciprocal Rank across query results."""
    if not eval_results:
        return 0.0
    rr_sum = 0.0
    for res in eval_results:
        expected_chapter = res.get("expected_chapter")
        citations = res.get("citations", [])
        reciprocal_rank = 0.0
        for rank, c in enumerate(citations, start=1):
            if c.get("chapter_index") == expected_chapter:
                reciprocal_rank = 1.0 / rank
                break
        rr_sum += reciprocal_rank
    return rr_sum / len(eval_results)

