"""Citation and claim validation service."""

from typing import List, Dict, Any


class CitationValidator:
    def validate_citation(self, claim_text: str, source_content: str) -> bool:
        """Verifies claim tokens are grounded in the source text."""
        if not source_content:
            return False
        # Simple token presence check
        claim_words = set(claim_text.lower().split())
        source_words = set(source_content.lower().split())
        overlap = claim_words.intersection(source_words)
        return len(overlap) >= len(claim_words) * 0.3
