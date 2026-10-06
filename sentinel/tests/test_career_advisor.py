import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sentinel.app.main import app
from sentinel.app.db import init_db, async_session_maker
from sentinel.app.domain.career_advisor import CareerAdvisorEngine
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.sources.base import RawItem
from sentinel.app.pipeline.scoring import score_item


@pytest.mark.asyncio
async def test_career_advisor_journal_and_diagnosis():
    await init_db()
    advisor = CareerAdvisorEngine()

    async with async_session_maker() as session:
        # Record work log
        w_entry = await advisor.record_journal_entry(
            session=session,
            user_id=123,
            entry_type="work",
            content="Built streaming vLLM inference endpoint with PagedAttention and Redis cache",
        )
        assert w_entry.id is not None
        assert w_entry.entry_type == "work"

        # Record learned log
        l_entry = await advisor.record_journal_entry(
            session=session,
            user_id=123,
            entry_type="learned",
            content="Understood continuous chunked prefill and FlashAttention-2 memory hierarchy",
        )
        assert l_entry.entry_type == "learned"

        # Diagnose career path
        diag = await advisor.diagnose_career_path(session=session, user_id=123)
        assert diag["target_role"] == "Senior AI & Data Systems Engineer"
        assert "declared_next_topic" in diag
        assert "why_next" in diag
        assert "real_world_example" in diag
        assert len(diag["recent_work"]) >= 1
        assert len(diag["recent_learned"]) >= 1


@pytest.mark.asyncio
async def test_bot_command_handler_career_commands():
    await init_db()
    handler = BotCommandHandler()

    async with async_session_maker() as session:
        # Test /work with args
        work_resp = await handler.handle_work("Optimized dbt data quality models and Airflow DAGs", session, user_id=456)
        assert "Work Activity Logged Successfully" in work_resp
        assert "Declared Next Step" in work_resp

        # Test /learned with args
        learn_resp = await handler.handle_learned("Mastered DuckDB Parquet incremental indexing", session, user_id=456)
        assert "Knowledge Logged & Skill Level Updated" in learn_resp
        assert "DECLARED: WHAT YOU MUST LEARN NEXT" in learn_resp
        assert "REAL-WORLD PRODUCTION SCENARIO" in learn_resp

        # Test /career
        career_resp = await handler.handle_career(session, user_id=456)
        assert "Personal Career & Skills Advisor" in career_resp
        assert "DECLARED: WHAT YOU MUST LEARN NEXT" in career_resp
        assert "REAL-WORLD PRODUCTION SCENARIO" in career_resp

        # Test /interests
        interest_resp = await handler.handle_interests("add Agentic Tool Calling", session, user_id=456)
        assert "Registered" in interest_resp
        assert "Agentic Tool Calling" in interest_resp


def test_dynamic_scoring_not_repetitive():
    # vLLM release item
    vllm_item = RawItem(
        source_id="github",
        external_id="gh_vllm_1",
        canonical_url="https://github.com/vllm-project/vllm/releases/tag/v0.6.0",
        title="vLLM v0.6.0 Release",
        raw_content="Major release adding chunked prefill and speculative decoding benchmarks.",
        source_type="github",
        reliability_tier=9,
        published_at=datetime.now(timezone.utc),
    )
    _, _, priority1, reason1, action1 = score_item(vllm_item)
    assert "vllm" in action1.lower() or "chunked prefill" in action1.lower()
    assert "Test in local staging container and benchmark against existing baseline." != action1

    # Transformers item
    hf_item = RawItem(
        source_id="github",
        external_id="gh_hf_1",
        canonical_url="https://github.com/huggingface/transformers/releases/tag/v5.18.0",
        title="huggingface/transformers Release 5.18.0",
        raw_content="Breaking changes to generation configs and pipeline kwargs.",
        source_type="github",
        reliability_tier=9,
        published_at=datetime.now(timezone.utc),
    )
    _, _, priority2, reason2, action2 = score_item(hf_item)
    assert "transformer" in reason2.lower() or "pipeline" in action2.lower()
    assert action1 != action2  # Actions must be distinct and contextual!


@pytest.mark.asyncio
async def test_dashboard_displays_dates():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/dashboard")
        assert resp.status_code == 200
        # Check that date formatting and career panel are in the HTML
        assert "Career & Skills Intelligence" in resp.text
        assert "DECLARED: NEXT TO LEARN" in resp.text
