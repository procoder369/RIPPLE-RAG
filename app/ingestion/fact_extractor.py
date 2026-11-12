"""Extracts narrative facts, entities, and states from chapter chunks."""

import re
from typing import List, Dict, Any, Optional
from app.core.logging import logger


class FactExtractor:
    """Extracts proposed story facts, character states, and relationships."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def extract_from_chunk(
        self,
        chunk_text: str,
        chapter_index: int,
        known_characters: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extracts atomic facts and character states from chunk text.
        Returns a list of structured fact dictionaries.
        """
        facts: List[Dict[str, Any]] = []

        # If LLM client is configured and not in pure offline mock mode, invoke LLM
        if self.llm_client and hasattr(self.llm_client, "extract_facts"):
            try:
                llm_facts = self.llm_client.extract_facts(chunk_text, chapter_index)
                if llm_facts:
                    return llm_facts
            except Exception as exc:
                logger.warning(f"LLM fact extraction failed: {exc}. Falling back to heuristic extractor.")

        # Heuristic extraction for narrative statements
        # Matches capitalized potential character names and actions
        sentences = re.split(r"(?<=[.!?])\s+", chunk_text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue

            # Look for state changes or key narrative actions (e.g., killed, died, allied, lost, held)
            action_match = re.search(
                r"\b([A-Z][a-z]+)\s+(discovered|killed|died|fell into|allied with|betrayed|lost|wields|obtained|married|became|left|held|defended|ordered|was dead)\s*([^,.;]*)",
                sent_clean,
                re.IGNORECASE,
            )
            if action_match:
                subject, verb, obj = action_match.groups()
                stmt = f"{subject} {verb} {obj.strip()}".strip() if obj else f"{subject} {verb}"
                facts.append({
                    "entity_name": subject.capitalize(),
                    "statement": stmt,
                    "category": "state_change",
                    "source_quote": sent_clean,
                    "confidence": 0.85,
                })

        return facts

