"""Continuity analysis and contradiction detection."""

import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import ContinuityViolation
from app.continuity.rules_engine import DeterministicRulesEngine
from app.retrieval.graph_retriever import GraphRetriever
from app.generation.prompt_builder import PromptBuilder
from app.generation.llm_client import LLMClient


class ContradictionDetector:
    """Detects plot holes, timeline paradoxes, and character status violations."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def analyze_manuscript(
        self,
        db: Session,
        story_id: str,
        chapter_index: int,
        text: str,
        mentioned_characters: List[str] = None,
    ) -> Dict[str, Any]:
        """Runs multi-tiered continuity audit on manuscript text."""
        violations: List[Dict[str, Any]] = []

        # 1. Deterministic Rule Checks
        if mentioned_characters:
            for char_name in mentioned_characters:
                rule_violation = DeterministicRulesEngine.check_character_state(
                    db=db,
                    story_id=story_id,
                    character_name=char_name,
                    target_chapter=chapter_index,
                    attempted_action=text[:200],
                )
                if rule_violation:
                    violations.append(rule_violation)

        # 2. Semantic LLM-based narrative check
        char_list = mentioned_characters or []
        graph_context = GraphRetriever.retrieve_entity_context(db, story_id, char_list)
        canon_statements = [f["statement"] for f in graph_context.get("canon_facts", [])]
        context_str = "\n".join(canon_statements) if canon_statements else "No prior facts recorded."

        prompt = PromptBuilder.build_continuity_prompt(context=context_str, manuscript_text=text)
        llm_response = self.llm_client.generate(prompt)

        try:
            # Extract JSON object substring if model includes markdown or preamble
            clean_resp = llm_response.strip()
            start_idx = clean_resp.find("{")
            end_idx = clean_resp.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                parsed = json.loads(clean_resp[start_idx:end_idx])
                if parsed.get("has_contradiction"):
                    violations.extend(parsed.get("violations", []))
        except Exception as exc:
            from app.core.logging import logger
            logger.warning(f"Could not parse LLM continuity response JSON: {exc}")

        # Persist violations
        for v in violations:
            violation_record = ContinuityViolation(
                story_id=story_id,
                violation_type=v.get("violation_type", "GENERAL_CONTRADICTION"),
                severity=v.get("severity", "WARNING"),
                description=v.get("description", "Potential plot contradiction detected"),
                suggested_fix=v.get("suggested_fix"),
            )
            db.add(violation_record)
        if violations:
            db.commit()

        return {
            "has_contradictions": len(violations) > 0,
            "total_violations": len(violations),
            "violations": violations,
        }

