"""Tests for Telegram bot command handlers and formatting."""

import pytest
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.bot.formatters import chunk_message, format_daily_digest
from sentinel.app.models import ItemModel


@pytest.mark.asyncio
async def test_bot_start_handler():
    handler = BotCommandHandler()
    msg = await handler.handle_start(user_id=123456789)
    assert "Syed" in msg
    assert "$0.00" in msg


@pytest.mark.asyncio
async def test_bot_why_and_compare_handlers():
    handler = BotCommandHandler()
    why_msg = await handler.handle_why("vLLM-PagedAttention")
    assert "Technical Breakdown" in why_msg or "vLLM" in why_msg

    cmp_msg = await handler.handle_compare("modelA modelB")
    assert "Model Comparison Analysis" in cmp_msg or "Architecture" in cmp_msg


@pytest.mark.asyncio
async def test_bot_hardware_and_fit_handlers():
    handler = BotCommandHandler()
    fit_msg = await handler.handle_fit("qwen2.5-7b")
    assert "Hardware Fit Analysis" in fit_msg
    assert "VRAM Budget" in fit_msg


@pytest.mark.asyncio
async def test_bot_work_and_win_handlers():
    handler = BotCommandHandler()
    work_msg = await handler.handle_work()
    assert "Work Context" in work_msg
    assert "vLLM" in work_msg

    win_msg = await handler.handle_win("Optimized query execution in dbt")
    assert "Work Win Logged" in win_msg


def test_chunk_message_splits_long_text():
    long_text = "Line\n" * 1500
    chunks = chunk_message(long_text, max_chars=1000)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 1000


def test_daily_digest_formatting_structure():
    item = ItemModel(
        source_id="test",
        external_id="1",
        canonical_url="https://example.com/item",
        title="vLLM v0.6 Released",
        importance_score=0.9,
        priority="MUST_KNOW",
        why_it_matters="Touches your day-job data & AI stack: vLLM",
        practical_action="Upgrade staging test container",
        epistemic_marker="✅",
    )
    digest = format_daily_digest([item], scanned_count=100, accepted_count=1)
    assert "AI ENGINEERING BRIEF" in digest
    assert "MUST KNOW" in digest
    assert "vLLM v0.6 Released" in digest
    assert "FOR YOUR WORK" in digest
    assert "TODAY'S LEARNING PRIORITY" in digest
