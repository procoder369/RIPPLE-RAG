"""Evaluation metrics for generation quality: Citation Precision and Grounding."""

import re
from typing import List, Dict, Any


def evaluate_groundedness(answer: str, context_text: str) -> float:
    """Measures keyword overlap between generated answer and provided context."""
    if not answer or not context_text:
        return 0.0
    ans_words = set(re.findall(r"\w+", answer.lower()))
    ctx_words = set(re.findall(r"\w+", context_text.lower()))
    if not ans_words:
        return 0.0
    overlap = len(ans_words.intersection(ctx_words))
    return overlap / len(ans_words)


def evaluate_citation_presence(answers: List[str]) -> float:
    """Calculates ratio of generated answers that contain explicit citation brackets."""
    if not answers:
        return 0.0
    cited = sum(1 for a in answers if "[Source #" in a or "[Canon Fact" in a)
    return cited / len(answers)

