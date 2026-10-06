"""Evidence and Trust Layer: Epistemic markers, Hype Detection, and Contradiction Detection."""

import re
from typing import Tuple, List, Optional
from sentinel.app.sources.base import RawItem

# Hype buzzwords commonly seen without empirical verification
HYPE_TRIGGERS = [
    r"\b100x\s+faster\b",
    r"\breplaces\s+all\s+(?:developers|engineers|models)\b",
    r"\brevolutionary\s+breakthrough\b",
    r"\bunmatched\s+sota\b",
    r"\bagi\s+achieved\b",
    r"\bkills\s+(?:gpt|claude|gemini)\b",
    r"\b10x\s+cheaper\b",
]


def evaluate_epistemic_level(item: RawItem) -> Tuple[str, str]:
    """
    Assigns epistemic marker and confidence label.
    - Verified fact ✅: Primary source (tier >= 9) + release notes/model card with weights.
    - Source claim 📣: Self-reported lab post or blog.
    - Inference 🧩: Synthesized logic.
    - Recommendation 🎯: System action recommendation.
    - Uncertainty ❓: Low tier or missing validation.
    """
    text = f"{item.title} {item.raw_content}".lower()

    if item.reliability_tier >= 9:
        if any(w in text for w in ["release", "weights released", "github", "v0.", "v1.", "v2."]):
            return "✅", "VERIFIED_FACT"
        return "📣", "SOURCE_CLAIM"
    elif item.reliability_tier >= 6:
        return "📣", "SOURCE_CLAIM"
    else:
        return "❓", "UNCERTAINTY"


def detect_hype(item: RawItem) -> Tuple[bool, Optional[str]]:
    """
    Flags potential marketing hype when extreme claims lack reproducible benchmark citations.
    """
    text = f"{item.title} {item.raw_content}".lower()
    for trigger in HYPE_TRIGGERS:
        if re.search(trigger, text):
            # Check if an independent verifiable benchmark link or source accompanies it
            has_verification = any(w in text for w in [
                "arxiv.org", "github.com/", "huggingface.co/spaces",
                "reproducible code", "independent evaluation", "verified benchmark",
            ])
            if not has_verification:
                return True, f"Sensational claim detected without verifiable benchmark citation: '{trigger}'"
    return False, None


def detect_contradiction(claim_a: str, claim_b: str) -> Tuple[bool, Optional[str]]:
    """
    Checks for conflicting numeric claims regarding context window or parameter count.
    """
    ctx_pattern = re.compile(r"(\d+)[kK]\s+context")
    match_a = ctx_pattern.search(claim_a)
    match_b = ctx_pattern.search(claim_b)

    if match_a and match_b:
        val_a = int(match_a.group(1))
        val_b = int(match_b.group(1))
        if val_a != val_b:
            return True, f"Conflicting context window claimed: {val_a}k vs {val_b}k."
            
    return False, None
