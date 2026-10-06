import pytest
from datetime import datetime, timezone
from sqlalchemy.future import select
from sentinel.app.db import init_db, async_session_maker
from sentinel.app.models import ChatMessageModel, UserMemoryModel
from sentinel.app.domain.conversation import ConversationEngine
from sentinel.app.bot.handlers import BotCommandHandler


@pytest.mark.asyncio
async def test_conversation_engine_chat_and_auto_memory():
    await init_db()
    conv_engine = ConversationEngine()

    async with async_session_maker() as session:
        # 1. First turn: user shares a preference with a memory trigger
        msg1 = "Remember that I prefer vLLM and PyTorch for all local inference on my RTX 4060."
        reply1 = await conv_engine.chat(session, user_id=999, user_message=msg1)
        assert reply1 is not None
        assert len(reply1) > 0

        # Check that user memory was automatically extracted and saved
        memories = await conv_engine.get_memories(session, user_id=999)
        assert len(memories) >= 1
        assert any("vllm" in m.memory_text.lower() for m in memories)

        # 2. Second turn: continuing conversation
        msg2 = "What quantization format should I use for a 8B model?"
        reply2 = await conv_engine.chat(session, user_id=999, user_message=msg2)
        assert reply2 is not None

        # Verify chat messages were saved to the database
        stmt = select(ChatMessageModel).where(ChatMessageModel.user_id == 999)
        res = await session.execute(stmt)
        turns = list(res.scalars().all())
        assert len(turns) >= 4  # 2 user turns + 2 assistant turns


@pytest.mark.asyncio
async def test_memory_and_clear_command_handlers():
    await init_db()
    handler = BotCommandHandler()

    async with async_session_maker() as session:
        # Test adding a memory explicitly
        add_resp = await handler.handle_memory("add I am building a realtime computer vision pipeline", session, user_id=888)
        assert "Saved to long-term memory" in add_resp

        # Test listing memories
        list_resp = await handler.handle_memory("", session, user_id=888)
        assert "Sentinel Long-Term AI Memory" in list_resp
        assert "realtime computer vision pipeline" in list_resp

        # Test conversation handler
        chat_resp = await handler.handle_conversation("How should I optimize video frames?", session, user_id=888)
        assert len(chat_resp) > 0

        # Test clearing history
        clear_hist_resp = await handler.handle_clear(session, user_id=888)
        assert "Chat history reset" in clear_hist_resp

        # Test clearing memories
        clear_mem_resp = await handler.handle_memory("clear", session, user_id=888)
        assert "Cleared" in clear_mem_resp


@pytest.mark.asyncio
async def test_role_intake_interview_and_job_extraction():
    await init_db()
    conv_engine = ConversationEngine()

    async with async_session_maker() as session:
        # Step 1: User says their role
        role_msg = "I am a Data and AI Engineer"
        reply1 = await conv_engine.chat(session, user_id=777, user_message=role_msg)
        # Should ask the 3 follow-up questions about workloads, data stack, and bottlenecks
        assert "Core Workload" in reply1
        assert "Data & Serving Stack" in reply1
        assert "Current Bottlenecks" in reply1

        # Step 2: User explains what they do in their job
        job_msg = "In my job I build streaming vLLM inference endpoints, optimize TTFT latency, and maintain Airflow DAGs with dbt and Postgres."
        reply2 = await conv_engine.chat(session, user_id=777, user_message=job_msg)
        assert reply2 is not None

        # Verify job context was saved into memory
        memories = await conv_engine.get_memories(session, user_id=777)
        assert any("vllm" in m.memory_text.lower() or "airflow" in m.memory_text.lower() for m in memories)


@pytest.mark.asyncio
async def test_auto_model_comparison():
    from sentinel.app.domain.comparison import ComparisonEngine
    comp_engine = ComparisonEngine()

    result = await comp_engine.auto_compare_model_release("Qwen-2.5-Coder-7B", baseline="LLaMA-3.1-8B", user_vram_gb=8.0)
    assert result is not None
    assert len(result) > 0
    assert "Comparison" in result or "Pros" in result or "Model" in result

