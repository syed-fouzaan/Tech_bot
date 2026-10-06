"""Standup Soundbite / 45-Second Tech Take Generator.

Compresses dense AI papers, models, or data architecture concepts into a
crisp, natural 45-second conversational soundbite tailored for morning standup
or casual 1:1 discussions with tech leads.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class StandupSoundbiteEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def generate_soundbite(self, topic: str) -> str:
        """Synthesizes a 45-second spoken elevator pitch for standup or meetings."""
        clean = topic.strip()
        if not clean:
            return (
                "🎙️ **Standup Soundbite / 45-Second Tech Take**\n\n"
                "Get a sharp, conversational 45-second speaking script for your team standup or 1:1:\n"
                "Usage: `/soundbite <topic or technology>`\n\n"
                "Examples:\n"
                "• `/soundbite Speculative Decoding`\n"
                "• `/soundbite DeepSeek-V3 MoE architecture`\n"
                "• `/soundbite DuckDB vs Polars for data lakes`\n"
                "• `/soundbite FlashAttention-3 FP8`"
            )

        system_prompt = (
            "You are a Senior/Staff AI & Data Engineer preparing a 45-second verbal update for your morning standup or tech sync.\n"
            "Format the response into a spoken conversational script that sounds effortless, highly knowledgeable, and free of academic jargon:\n\n"
            "🎙️ **THE 45-SECOND SPOKEN SCRIPT**\n"
            "(Write verbatim what to say out loud to your teammates or manager in 3-4 natural sentences)\n\n"
            "🧠 **THE CORE TECHNICAL TAKE**\n"
            "(The single sharpest technical insight you can drop to demonstrate deep architectural understanding)\n\n"
            "⚠️ **THE SKEPTICAL CAVEAT**\n"
            "(The real-world caveat or failure mode that prevents naive adoption)\n\n"
            "Keep the tone natural, authoritative, and practical."
        )

        prompt = f"Generate a 45-second standup soundbite and technical take for: {clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            f"🎙️ **Standup Soundbite: {clean}**\n\n"
            f"{response.content}"
        )
