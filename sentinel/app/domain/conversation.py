"""Conversational AI Engine with Multi-Turn History and Long-Term Memory.

Maintains multi-turn context, remembers user facts, preferences, and stack details,
and responds as an uncompromising Staff AI Systems Architect & Pair Programmer.
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import ChatMessageModel, UserMemoryModel
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
        1. Auto-extracts any memory cues (e.g. 'remember that...')
        2. Retrieves long-term memories & recent chat history
        3. Formulates context-rich prompt and generates response
        4. Saves turns to persistent database
        """
        clean_msg = user_message.strip()
        if not clean_msg:
            return "How can I help you today with your AI and data engineering systems?"

        # 1. Auto-extract memory cues
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
            f"## Instructions:\n"
            f"- Speak naturally, pragmatically, and conversationally like a senior teammate.\n"
            f"- Remember and reference facts they told you earlier.\n"
            f"- Give rigorous, production-grade technical advice with concrete examples.\n"
            f"- Calibrate any local suggestions to their RTX 4060 (8GB VRAM).\n"
            f"- Keep responses concise and focused on high-signal engineering reality."
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
