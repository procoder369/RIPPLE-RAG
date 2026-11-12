"""Processes writer queries and extracts entity mentions and temporal constraints."""

import re
from typing import Dict, Any, List


class QueryProcessor:
    """Analyzes questions about story lore, continuity, or what-if scenarios."""

    @staticmethod
    def process_query(query_text: str) -> Dict[str, Any]:
        """Extracts search keywords, capitalized entity candidates, and chapter references."""
        # Detect chapter mentions e.g. "chapter 3", "ch. 5"
        chapter_match = re.search(r"\b(?:chapter|ch\.?)\s*(\d+)", query_text, re.IGNORECASE)
        target_chapter = int(chapter_match.group(1)) if chapter_match else None

        # Extract potential named entities (capitalized words)
        words = query_text.split()
        potential_entities: List[str] = []
        for word in words:
            cleaned = re.sub(r"[^\w]", "", word)
            if cleaned and cleaned[0].isupper() and cleaned.lower() not in {"what", "when", "where", "why", "who", "did", "how", "is", "was", "the", "in", "chapter"}:
                potential_entities.append(cleaned)

        return {
            "original_query": query_text,
            "target_chapter": target_chapter,
            "entity_mentions": list(set(potential_entities)),
            "clean_query": query_text.strip(),
        }

