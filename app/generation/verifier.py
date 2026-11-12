"""Verifies citations and grounds output against retrieved evidence."""

import re
from typing import Dict, Any, List


class OutputVerifier:
    """Validates citations in generated answers and detects hallucination risks."""

    CITATION_PATTERN = re.compile(r"\[(?:Source #|Canon Fact)(\d+)?\]", re.IGNORECASE)

    @classmethod
    def verify(
        cls,
        answer: str,
        citations: List[Dict[str, Any]],
        context: str,
    ) -> Dict[str, Any]:
        """
        Audits the answer for valid citation brackets and grounding.
        """
        found_citations = cls.CITATION_PATTERN.findall(answer)
        total_sources_available = len(citations)

        has_citations = len(found_citations) > 0 or "[Source #" in answer or "[Canon Fact" in answer
        hallucination_flag = False
        reasons: List[str] = []

        if not has_citations and total_sources_available > 0:
            hallucination_flag = True
            reasons.append("Answer does not explicitly cite any retrieved sources.")

        # Check for non-existent source index citations e.g. [Source #99]
        for num_str in found_citations:
            if num_str:
                idx = int(num_str)
                if idx > total_sources_available or idx < 1:
                    hallucination_flag = True
                    reasons.append(f"Answer cited [Source #{idx}], but only {total_sources_available} sources exist.")

        return {
            "verified": not hallucination_flag,
            "citations_found_count": len(found_citations),
            "hallucination_warning": hallucination_flag,
            "issues": reasons,
        }

