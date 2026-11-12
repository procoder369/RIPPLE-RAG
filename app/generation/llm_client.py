"""LLM client adapter supporting Claude, OpenAI, Gemini, and Mock mode."""

import json
from typing import Dict, Any, List
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class LLMClient:
    """Dispatches generation requests to configured LLM providers with robust fallbacks."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL

    def generate(self, prompt: str, temperature: float = None) -> str:
        """Generates text completion based on prompt."""
        temp = temperature if temperature is not None else settings.LLM_TEMPERATURE

        if self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                message = client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    temperature=temp,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text
            except Exception as exc:
                logger.error(f"Anthropic API call failed: {exc}. Falling back to mock generator.")

        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=self.model,
                    temperature=temp,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                logger.error(f"OpenAI API call failed: {exc}. Falling back to mock generator.")

        # Default Mock Generation for testing & development
        return self._generate_mock_response(prompt)

    def extract_facts(self, chunk_text: str, chapter_index: int) -> List[Dict[str, Any]]:
        """Invokes structured extraction for chapter facts."""
        # If in mock mode, return an empty list to let heuristic fallback run
        if self.provider == "mock":
            return []

        from app.generation.prompt_builder import PromptBuilder
        prompt = PromptBuilder.build_extraction_prompt(chunk_text, chapter_index)
        response_text = self.generate(prompt)
        try:
            # Parse json block
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start != -1 and end != 0:
                return json.loads(response_text[start:end])
        except Exception as exc:
            logger.warning(f"Could not parse LLM extraction JSON: {exc}")
        return []

    def _generate_mock_response(self, prompt: str) -> str:
        """Deterministic response synthesizer for mock mode."""
        if "story_qa" in prompt or "Writer's Question" in prompt:
            # Extract query and check if context has evidence
            if "=== MANUSCRIPT EXCERPTS ===" in prompt:
                return (
                    "Based on the manuscript excerpts, the events indicate that this occurs in Chapter 1. "
                    "According to [Source #1], the sequence of events is confirmed by the narrative text."
                )
            return "This event is not documented in the current manuscript or canon."

        if "continuity_check" in prompt:
            return json.dumps({
                "has_contradiction": False,
                "violations": [],
            })

        return "Synthesized RippleRAG narrative response."

