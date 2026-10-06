"""Conversational AI Engine with Multi-Turn History and Long-Term Memory.

Maintains multi-turn context, remembers user facts, preferences, and stack details,
and responds as an uncompromising Staff AI Systems Architect & Pair Programmer.
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import ChatMessageModel, UserMemoryModel, UserJournalModel
from sentinel.app.domain.profile import get_default_profile, UserProfile
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


# Heuristics to auto-capture memorable facts from natural conversation
MEMORY_TRIGGERS = [
    r"remember\s+that\s+(.*)",
    r"i\s+prefer\s+(.*)",
    r"i\s+like\s+(.*)",
    r"i\s+work\s+with\s+(.*)",
    r"i\s+am\s+building\s+(.*)",
    r"i'm\s+building\s+(.*)",
    r"i\s+use\s+(.*)",
    r"my\s+goal\s+is\s+(.*)",
    r"my\s+target\s+is\s+(.*)",
    r"we\s+use\s+(.*)",
]

STACK_DETECTION_KEYWORDS = [
    "vllm", "airflow", "dbt", "pytorch", "fastapi", "postgres", "sql", "duckdb",
    "polars", "rag", "langgraph", "docker", "redis", "kafka", "spark", "opencv",
    "yolo", "latency", "pipeline", "serving", "inference", "etl", "models", "endpoint"
]


class ConversationEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def get_memories(self, session: AsyncSession, user_id: int) -> List[UserMemoryModel]:
        """Retrieves all long-term memories for a user."""
        stmt = (
            select(UserMemoryModel)
            .where(UserMemoryModel.user_id == user_id)
            .order_by(UserMemoryModel.created_at.asc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def add_memory(
        self,
        session: AsyncSession,
        user_id: int,
        memory_text: str,
        category: str = "fact",
    ) -> UserMemoryModel:
        """Stores a persistent long-term memory fact."""
        clean_text = memory_text.strip()
        mem = UserMemoryModel(
            user_id=user_id,
            memory_text=clean_text,
            category=category,
            created_at=datetime.now(timezone.utc),
        )
        session.add(mem)
        await session.commit()
        await session.refresh(mem)
        return mem

    async def clear_memories(self, session: AsyncSession, user_id: int) -> int:
        """Deletes all stored long-term memories for a user."""
        stmt = select(UserMemoryModel).where(UserMemoryModel.user_id == user_id)
        res = await session.execute(stmt)
        mems = list(res.scalars().all())
        for m in mems:
            await session.delete(m)
        await session.commit()
        return len(mems)

    async def clear_history(self, session: AsyncSession, user_id: int) -> int:
        """Clears recent conversational turn history."""
        stmt = select(ChatMessageModel).where(ChatMessageModel.user_id == user_id)
        res = await session.execute(stmt)
        msgs = list(res.scalars().all())
        for m in msgs:
            await session.delete(m)
        await session.commit()
        return len(msgs)

    async def auto_extract_memories(self, session: AsyncSession, user_id: int, user_text: str) -> Optional[str]:
        """Extracts and saves key facts or preferences if detected in message."""
        text_lower = user_text.lower().strip()
        for pattern in MEMORY_TRIGGERS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                captured = match.group(1).strip()
                if len(captured) > 3:
                    await self.add_memory(session, user_id, f"User stated: {captured}", category="preference")
                    return captured
        return None

    async def chat(
        self,
        session: AsyncSession,
        user_id: int,
        user_message: str,
    ) -> str:
        """
        Processes a conversational message:
        1. Auto-detects role intake statements and triggers deep questionnaire
        2. Auto-extracts memory cues and job details
        3. Formulates context-rich prompt and generates response
        4. Saves turns to persistent database
        """
        clean_msg = user_message.strip()
        if not clean_msg:
            return "How can I help you today with your AI and data engineering systems?"

        # Check for role statement intake trigger
        role_pattern = r"\b(i am|i'm|my role is|work as)?\s*(a\s+)?(data\s+(and|&)\s+ai\s+engineer|ai\s+(and|&)\s+data\s+engineer|data\s+engineer|ai\s+engineer|ml\s+engineer)\b"
        is_role_statement = bool(re.search(role_pattern, clean_msg, re.IGNORECASE))
        has_extended_job_details = len(clean_msg.split()) >= 15

        if is_role_statement and not has_extended_job_details:
            reply = (
                f"🎯 **Awesome, {self.profile.name}!**\n\n"
                "As your Staff AI & Data Engineering mentor, I want to calibrate everything directly to your day-to-day systems. "
                "Tell me a bit more about what you do in your job:\n\n"
                "1. ⚙️ **Core Workload**: Are you primarily building real-time LLM inference endpoints (vLLM, Ollama), fine-tuning models, or orchestrating data pipelines (Airflow, dbt)?\n"
                "2. 🗄️ **Data & Serving Stack**: What databases, streaming queues, and vector stores are in your active production systems?\n"
                "3. ⚡ **Current Bottlenecks**: What is your team's biggest headache right now (e.g. inference latency/TTFT, GPU VRAM fragmentation, schema drift, evals)?\n\n"
                "Explain everything you do, and I'll extract and structure your technical profile!"
            )
            bot_turn = ChatMessageModel(
                user_id=user_id,
                role="assistant",
                content=reply,
                created_at=datetime.now(timezone.utc),
            )
            session.add(bot_turn)
            await self.add_memory(session, user_id, "Role: Data and AI Engineer", category="work")
            await session.commit()
            return reply

        # Auto-extract job details if user is describing their work
        msg_lower = clean_msg.lower()
        matched_tools = [k for k in STACK_DETECTION_KEYWORDS if k in msg_lower]
        if len(matched_tools) >= 2 and ("job" in msg_lower or "work" in msg_lower or "build" in msg_lower or "pipeline" in msg_lower):
            await self.add_memory(
                session,
                user_id,
                f"Day-Job Work Context: {clean_msg[:200]}",
                category="work",
            )
            journal_entry = UserJournalModel(
                user_id=user_id,
                entry_type="work",
                content=clean_msg,
                tags=", ".join(matched_tools[:5]),
                created_at=datetime.now(timezone.utc),
            )
            session.add(journal_entry)
            await session.commit()

        # 1. Auto-extract memory cues (e.g. 'remember that...')
        extracted_fact = await self.auto_extract_memories(session, user_id, clean_msg)

        # 2. Save user message to database
        user_turn = ChatMessageModel(
            user_id=user_id,
            role="user",
            content=clean_msg,
            created_at=datetime.now(timezone.utc),
        )
        session.add(user_turn)
        await session.commit()

        # 3. Retrieve long-term memories
        memories = await self.get_memories(session, user_id)
        memories_text = "\n".join([f"- {m.memory_text}" for m in memories]) if memories else "No explicit custom memories saved yet."

        # 4. Retrieve recent conversation history (last 8 turns)
        hist_stmt = (
            select(ChatMessageModel)
            .where(ChatMessageModel.user_id == user_id)
            .order_by(ChatMessageModel.created_at.desc())
            .limit(8)
        )
        hist_res = await session.execute(hist_stmt)
        recent_turns = list(reversed(list(hist_res.scalars().all())))

        formatted_history = []
        for turn in recent_turns[:-1]:  # Exclude current message
            prefix = "User" if turn.role == "user" else "Assistant"
            formatted_history.append(f"{prefix}: {turn.content}")
        history_context = "\n".join(formatted_history) if formatted_history else "(Beginning of conversation)"

        # 5. Build System Prompt with Long-Term Memory
        system_prompt = (
            f"You are Sentinel, a Senior Staff AI & Data Systems Engineer, pair programmer, and personal career mentor to {self.profile.name}.\n"
            f"You are having a continuous natural conversation with the engineer.\n\n"
            f"## Engineer Profile & Ground Truth:\n"
            f"- Role: {self.profile.role} at {self.profile.work_context.company_abstract}\n"
            f"- Target Role: {self.profile.target_role}\n"
            f"- Local Hardware: {self.profile.hardware.get('local_gpu')}, {self.profile.hardware.get('ram')}\n"
            f"- Production Stack: {', '.join(self.profile.work_context.stack)}\n\n"
            f"## Long-Term Memory (Facts Remembered from Past Turns):\n"
            f"{memories_text}\n\n"
            f"## Specialized Response Directives (MANDATORY):\n"
            f"1. STRUCTURED JOB INTAKE: When the user explains what they do in their job, extract and present a structured summary (Core Workloads, Active Stack, Pain Points) and confirm it is stored in working memory.\n"
            f"2. RESEARCH PAPERS (NO BULK JARGON): Never dump raw papers or mathematical abstracts. For any paper discussed, explain:\n"
            f"   • 🎯 Exact Aim: What core technical problem or limitation does it break?\n"
            f"   • 🔬 What It Contains: The concrete architectural mechanism in plain English.\n"
            f"   • 🛠️ How It Directly Helps YOUR Projects: Concrete application to the user's stack (e.g. vLLM, RTX 4060 8GB, Airflow/dbt). Never give academic fluff.\n"
            f"3. AUTOMATIC MODEL COMPARISON (PROS & CONS): Whenever any AI model is mentioned or released, AUTO-COMPARE it with the industry incumbent baseline (e.g. LLaMA-3.1-8B, Mistral-7B) without waiting for the user to ask. Detail 🟢 Pros and 🔴 Cons, and provide an exact hardware fit verdict for RTX 4060 (8GB VRAM).\n"
            f"4. 10:00 AM MORNING INTELLIGENCE: The bot automatically compiles and delivers high-signal daily briefs every day at 10:00 AM IST.\n"
            f"5. TONE: Pragmatic, Senior Staff Engineer, conversational, concise, and direct."
        )

        full_prompt = (
            f"## Recent Conversation:\n{history_context}\n\n"
            f"User: {clean_msg}\n\n"
            f"Assistant:"
        )

        # 6. Call AI Gateway
        response = await self.gateway.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            task=TaskType.CHAT,
        )
        assistant_reply = response.content

        # If we auto-captured a memory, append a brief subtle note
        if extracted_fact and "remember" in clean_msg.lower():
            if "remember" not in assistant_reply.lower() and "memory" not in assistant_reply.lower():
                assistant_reply += f"\n\n*(🧠 Saved to long-term memory: '{extracted_fact}')*"

        # 7. Save assistant reply to database
        bot_turn = ChatMessageModel(
            user_id=user_id,
            role="assistant",
            content=assistant_reply,
            created_at=datetime.now(timezone.utc),
        )
        session.add(bot_turn)
        await session.commit()

        return assistant_reply
