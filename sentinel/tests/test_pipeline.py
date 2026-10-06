"""Tests for pipeline: URL canonicalization, deduplication, scoring, and trust detection."""

import pytest
from datetime import datetime, timezone
from sentinel.app.sources.base import RawItem
from sentinel.app.pipeline.deduplication import canonicalize_url, compute_content_hash, cluster_items
from sentinel.app.pipeline.scoring import score_item
from sentinel.app.pipeline.trust import evaluate_epistemic_level, detect_hype, detect_contradiction


def test_url_canonicalization():
    raw_url = "https://huggingface.co/Qwen/Qwen2.5-7B?utm_source=twitter&utm_medium=social&ref=ai_bot#overview"
    clean = canonicalize_url(raw_url)
    assert "utm_source" not in clean
    assert "ref" not in clean
    assert clean == "https://huggingface.co/qwen/qwen2.5-7b"


def test_content_hash_consistency():
    url = "https://github.com/vllm-project/vllm/releases/tag/v0.6.0"
    title1 = "vLLM v0.6.0 Release: Enhanced PagedAttention"
    title2 = "vLLM v0.6.0 release:   enhanced pagedattention"
    
    h1 = compute_content_hash(url, title1)
    h2 = compute_content_hash(url, title2)
    assert h1 == h2


def test_cluster_items_near_duplicates():
    item1 = RawItem(
        source_id="github",
        external_id="1",
        canonical_url="https://github.com/vllm-project/vllm/releases/tag/v0.6.0",
        title="vLLM v0.6.0 Release: Enhanced PagedAttention",
        source_type="release",
        reliability_tier=9,
    )
    item2 = RawItem(
        source_id="rss_blogs",
        external_id="2",
        canonical_url="https://blog.example.com/vllm-v06-announcement",
        title="vLLM v0.6.0 Released with Enhanced PagedAttention",
        source_type="blog",
        reliability_tier=7,
    )
    clusters = cluster_items([item1, item2], threshold=0.6)
    assert len(clusters) == 1
    # Primary item should be item1 because tier 9 > tier 7
    assert clusters[0][0].reliability_tier == 9


def test_scoring_boosts_work_stack():
    work_item = RawItem(
        source_id="github",
        external_id="vllm-rel",
        canonical_url="https://github.com/vllm-project/vllm/releases",
        title="vLLM v0.6.2 Released with Airflow Operator and KV cache fix",
        source_type="release",
        reliability_tier=9,
        raw_content="Major performance fix reducing latency in production vLLM serving.",
    )
    importance, personal, priority, reasoning, action = score_item(work_item)
    assert priority == "MUST_KNOW"
    assert "day-job" in reasoning
    assert personal >= 0.7


def test_hype_detection():
    hype_item = RawItem(
        source_id="hn",
        external_id="123",
        canonical_url="https://news.ycombinator.com",
        title="New Open Model 100x Faster and Replaces All Engineers",
        source_type="discussion",
        reliability_tier=4,
        raw_content="This revolutionary breakthrough kills GPT and destroys all prior benchmarks.",
    )
    is_hype, reason = detect_hype(hype_item)
    assert is_hype
    assert "Sensational claim" in reason


def test_contradiction_detection():
    claim1 = "The model was trained with 128k context window support."
    claim2 = "Standard model card specifies 32k context length."
    is_contradiction, explanation = detect_contradiction(claim1, claim2)
    assert is_contradiction
    assert "128k vs 32k" in explanation
