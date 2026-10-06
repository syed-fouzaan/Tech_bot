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


def synthesize_practical_guidance(
    title: str,
    content: str,
    source_type: str,
    matched_work: List[str],
    matched_side: List[str],
    has_security: bool,
    has_major_release: bool,
) -> Tuple[str, str]:
    """
    Synthesizes rich, context-aware reasoning and a concrete real-world action.
    Eliminates repetitive taglines and generic boilerplate.
    """
    full_text = f"{title.lower()} {content.lower()}"

    # 1. Critical Security Vulnerability
    if has_security:
        pkg = matched_work[0] if matched_work else "affected package"
        reason = f"Security Advisory: Potential vulnerability detected touching {pkg} in your environment."
        action = f"Real-world action: Audit your active environment via `pip audit`. Inspect CVE details and patch `{pkg}` immediately in your requirements and Docker container."
        return reason, action

    # 2. vLLM / Inference Serving
    if "vllm" in full_text or "pagedattention" in full_text:
        reason = "Touches your day-job data & AI stack (vLLM): Directly impacts your production LLM inference engine, serving latency, and memory footprint."
        action = "Real-world action: Benchmark chunked prefill and KV-cache allocation under 16 concurrent requests on staging. Measure Time-To-First-Token (TTFT) and VRAM headroom before deploying."
        return reason, action

    # 3. Transformers / HuggingFace
    if "transformer" in full_text or "huggingface" in full_text:
        reason = "Touches your core model loading, tokenization, and pipeline execution foundation."
        action = "Real-world action: Review breaking changes in pipeline kwargs and tokenizer generation configs. Run regression tests on your local PyTorch serving scripts to verify zero API regressions."
        return reason, action

    # 4. Airflow / dbt / Data Pipelines
    if any(k in full_text for k in ["airflow", "dbt", "duckdb", "polars", "spark"]):
        matched = [k for k in ["airflow", "dbt", "duckdb", "polars", "spark"] if k in full_text]
        primary_k = matched[0].upper() if matched else "Data Pipeline"
        reason = f"Influences your data engineering pipelines, batch SLA reliability, and {primary_k} models."
        action = f"Real-world action: Run staging pipeline tests with `dbt test` or mock Airflow DAG runs. Validate incremental partition processing and schema contracts before merging to main."
        return reason, action

    # 5. Quantization / Edge Fit (AWQ, GGUF, EXL2)
    if any(k in full_text for k in ["quantiz", "awq", "gguf", "exl2", "bitsandbytes"]):
        reason = "Crucial for running frontier models locally on constrained GPU hardware (RTX 4060 8GB VRAM)."
        action = "Real-world action: Quantize the model weights with AutoAWQ or llama.cpp. Compare perplexity and tokens/second against FP16 baseline on your local 8GB card."
        return reason, action

    # 6. RAG / Vector Search / LangGraph / Agentic
    if any(k in full_text for k in ["rag", "langgraph", "agent", "vector", "embedding", "mcp"]):
        reason = "Directly applicable to your agentic workflows, contextual retrieval, and multi-turn tool calling."
        action = "Real-world action: Evaluate retrieval precision with hybrid BM25 + dense search. Run an automated eval suite (RAGAS) across 20 representative queries to verify groundedness."
        return reason, action

    # 7. Computer Vision / Edge (OpenCV, YOLO, MediaPipe)
    if any(k in full_text or k in title.lower() for k in ["opencv", "yolo", "cv", "image editing", "vision", "mediapipe"]):
        reason = "Aligns with your edge computer vision systems and real-time visual processing pipelines."
        action = "Real-world action: Benchmark frame processing throughput (FPS) and memory copies on video streams. Test TensorRT / ONNX Runtime export for 2-3x inference speedup."
        return reason, action

    # 8. PyTorch / Deep Learning Core
    if "pytorch" in full_text or "torch" in full_text:
        reason = "Foundational framework for all deep learning training and tensor operations in your stack."
        action = "Real-world action: Test CUDA 12.x kernel compatibility and `torch.compile` speedups on your RTX 4060. Verify memory allocator behavior under heavy batch loads."
        return reason, action

    # 9. arXiv Research Paper
    if "paper" in source_type or "arxiv" in source_type:
        reason = f"Fresh research paper exploring: {title[:75]}..."
        action = "Real-world action: Review the mathematical intuition in Section 3 and the ablation table. Implement a 50-line PyTorch prototype to verify claims before recommending for adoption."
        return reason, action

    # 10. General GitHub Release
    if "github" in source_type or has_major_release:
        reason = f"New release touching AI/data tooling: {title[:75]}"
        action = "Real-world action: Check release diff for breaking changes, deprecation notices, and pinned requirements before bumping your project dependency version."
        return reason, action

    # Default Contextual Fallback
    matched_tags = matched_work or matched_side or ["ecosystem development"]
    reason = f"Relevant to your AI/Data engineering stack: {', '.join(matched_tags[:3])}"
    action = f"Real-world action: Review architectural trade-offs; determine if performance benefits justify operational migration cost for your current systems."
    return reason, action


def score_item(
    item: RawItem,
    work_keywords: set = WORK_STACK_KEYWORDS,
    side_keywords: set = SIDE_PROJECT_KEYWORDS,
) -> Tuple[float, float, str, str, str]:
    """
    Computes (importance_score, personal_relevance_score, priority, reasoning, action)
    Formula:
      importance = technical_impact(0.20) + practical_value(0.20) + personal_relevance(0.25) + novelty(0.15) + industry_impact(0.10) + learning(0.10)
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
    if matched_work:
        personal_relevance += 0.4
    if matched_side:
        personal_relevance += 0.2

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
    if (importance >= 0.65 and matched_work) or (importance >= 0.75 and (has_security or item.reliability_tier >= 9)):
        priority = "MUST_KNOW"
    elif importance >= 0.55:
        priority = "SHOULD_KNOW"
    elif learning_value >= 0.7:
        priority = "LEARN"
    elif importance >= 0.40:
        priority = "WATCH"
    else:
        priority = "IGNORE"

    reasoning_text, action_text = synthesize_practical_guidance(
        title=item.title,
        content=item.raw_content,
        source_type=item.source_type,
        matched_work=matched_work,
        matched_side=matched_side,
        has_security=has_security,
        has_major_release=has_major_release,
    )

    return round(importance, 2), round(personal_relevance, 2), priority, reasoning_text, action_text
