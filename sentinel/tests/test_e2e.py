"""End-to-end integration test: Ingestion -> Pipeline -> Storage -> Telegram Daily Digest."""

import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sentinel.app.models import Base, ItemModel
from sentinel.app.sources.base import RawItem
from sentinel.app.pipeline.deduplication import canonicalize_url, compute_content_hash, cluster_items
from sentinel.app.pipeline.scoring import score_item
from sentinel.app.pipeline.trust import evaluate_epistemic_level, detect_hype
from sentinel.app.bot.handlers import BotCommandHandler


@pytest.mark.asyncio
async def test_full_e2e_ingestion_and_digest_flow():
    # 1. Setup isolated in-memory SQLite database
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Simulate raw ingested items from multiple sources
    mock_items = [
        RawItem(
            source_id="github",
            external_id="vllm-0.6.3",
            canonical_url="https://github.com/vllm-project/vllm/releases/tag/v0.6.3?utm_source=twitter",
            title="vLLM v0.6.3: Continuous Batching Performance Update",
            source_type="release",
            reliability_tier=9,
            raw_content="vLLM release with memory improvements and Airflow trigger support.",
        ),
        RawItem(
            source_id="arxiv",
            external_id="2409.12345",
            canonical_url="https://arxiv.org/abs/2409.12345",
            title="Efficient Attention Mechanics for Low-VRAM Serving",
            source_type="paper",
            reliability_tier=9,
            raw_content="Research on sub-quadratic attention for constrained edge devices.",
        ),
        RawItem(
            source_id="hackernews",
            external_id="9999",
            canonical_url="https://news.ycombinator.com/item?id=9999",
            title="Show HN: My New AI Tool that Replaces All Engineers",
            source_type="discussion",
            reliability_tier=4,
            raw_content="Revolutionary 100x faster tool.",
        ),
    ]

    # 3. Execute Pipeline Logic
    async with async_session() as session:
        for it in mock_items:
            it.canonical_url = canonicalize_url(it.canonical_url)
            importance, personal, priority, reasoning, action = score_item(it)
            marker, label = evaluate_epistemic_level(it)
            is_hype, _ = detect_hype(it)

            db_item = ItemModel(
                source_id=it.source_id,
                external_id=it.external_id,
                canonical_url=it.canonical_url,
                title=it.title,
                source_type=it.source_type,
                reliability_tier=it.reliability_tier,
                content_hash=compute_content_hash(it.canonical_url, it.title),
                importance_score=importance,
                personal_relevance_score=personal,
                priority=priority,
                summary=it.raw_content,
                why_it_matters=reasoning,
                practical_action=action,
                epistemic_marker=marker,
                hype_flag=is_hype,
            )
            session.add(db_item)
        await session.commit()

    # 4. Generate Daily Brief using Bot Command Handler
    handler = BotCommandHandler()
    async with async_session() as session:
        digest_output = await handler.handle_today(session)

    # 5. Assertions on the E2E Output
    assert "AI ENGINEERING BRIEF" in digest_output
    assert "vLLM v0.6.3" in digest_output
    assert "MUST KNOW" in digest_output
    assert "FOR YOUR WORK" in digest_output
    assert "✅" in digest_output or "📣" in digest_output

    await test_engine.dispose()
