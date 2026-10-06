"""Importance and personal relevance scoring engine."""

import re
from typing import Dict, List, Tuple
from sentinel.app.sources.base import RawItem

# User Profile Context (Syed - Data & AI Engineer at zig-zag.ai)
WORK_STACK_KEYWORDS = {
    "vllm", "airflow", "dbt", "pytorch", "transformers", "langgraph",
    "opencv", "mediapipe", "sql", "duckdb", "polars", "spark", "rag",
    "inference", "quantization", "gguf", "awq", "evals", "mcp"
}

SIDE_PROJECT_KEYWORDS = {
    "yolo", "cv", "computer vision", "fastapi", "react", "nextjs", "hackathon"
}


def score_item(
    item: RawItem,
    work_keywords: set = WORK_STACK_KEYWORDS,
    side_keywords: set = SIDE_PROJECT_KEYWORDS,
) -> Tuple[float, float, str, str, str]:
    """
    Computes (importance_score, personal_relevance_score, priority, reasoning, action)
    Formula:
      importance = technical_impact(0.25) + practical_value(0.25) + novelty(0.20) + industry_impact(0.15) + learning(0.15)
    """
    title_text = item.title.lower()
    content_text = item.raw_content.lower()
    full_text = f"{title_text} {content_text}"

    # Deterministic technical indicators
    has_major_release = any(w in full_text for w in ["v0.", "v1.", "v2.", "release", "breaking", "benchmark"])
    has_weights = any(w in full_text for w in ["weights", "apache", "open-source", "open-weight"])
    has_security = any(w in full_text for w in ["cve-", "vulnerability", "security", "patch"])

    technical_impact = 0.5
    if has_major_release:
        technical_impact += 0.25
    if has_weights:
        technical_impact += 0.2
    if has_security:
        technical_impact += 0.3
    technical_impact = min(technical_impact, 1.0)

    # Personal relevance: work stack vs side project
    matched_work = [k for k in work_keywords if re.search(rf"\b{re.escape(k)}\b", full_text)]
    matched_side = [k for k in side_keywords if re.search(rf"\b{re.escape(k)}\b", full_text)]

    personal_relevance = 0.4
    reasons = []

    if matched_work:
        personal_relevance += 0.4
        reasons.append(f"Touches your day-job data & AI stack: {', '.join(matched_work[:3])}")
    if matched_side:
        personal_relevance += 0.2
        reasons.append(f"Aligns with your portfolio and CV side projects: {', '.join(matched_side[:2])}")
    if has_security:
        reasons.append("Contains critical security/advisory impact")

    personal_relevance = min(personal_relevance, 1.0)
    practical_value = 0.7 if matched_work or has_major_release else 0.4
    novelty = 0.8 if "new" in full_text or "paper" in item.source_type else 0.5
    industry_impact = 0.8 if item.reliability_tier >= 9 else 0.5
    learning_value = 0.8 if ("paper" in item.source_type or "architecture" in full_text) else 0.5

    # Multi-factor weighted importance
    importance = (
        technical_impact * 0.20 +
        practical_value * 0.20 +
        personal_relevance * 0.25 +
        novelty * 0.15 +
        industry_impact * 0.10 +
        learning_value * 0.10
    )

    # Priority Classification
    # PRD §9: Work stack match + technical impact triggers MUST_KNOW
    if (importance >= 0.65 and matched_work) or (importance >= 0.75 and (has_security or item.reliability_tier >= 9)):
        priority = "MUST_KNOW"
        action = "Test in local staging container and benchmark against existing baseline."
    elif importance >= 0.55:
        priority = "SHOULD_KNOW"
        action = "Review documentation changes and note for architectural decisions."
    elif learning_value >= 0.7:
        priority = "LEARN"
        action = "Add core concepts to personal living roadmap."
    elif importance >= 0.40:
        priority = "WATCH"
        action = "Keep on radar; await independent benchmarks and stability."
    else:
        priority = "IGNORE"
        action = "Safe to ignore; low actionable relevance."

    reasoning_text = "; ".join(reasons) if reasons else "General AI ecosystem development"
    return round(importance, 2), round(personal_relevance, 2), priority, reasoning_text, action
