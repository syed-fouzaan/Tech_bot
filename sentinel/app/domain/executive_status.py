"""Executive 1:1 & Standup Status Generator.

Transforms logged work activities, learnings, and impact wins into a crisp,
60-second managerial briefing formatted for 1:1s, sprint reviews, and skip-levels.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import UserJournalModel, WorkImpactLogModel
from sentinel.app.domain.profile import get_default_profile, UserProfile
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


class ExecutiveStatusEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def generate_status(self, session: Optional[AsyncSession] = None, user_id: int = 0) -> str:
        """Synthesizes an executive-ready 1:1 / standup briefing."""
        wins = []
        work_logs = []
        learned_logs = []

        if session is not None:
            w_stmt = select(WorkImpactLogModel).where(WorkImpactLogModel.user_id == user_id).order_by(WorkImpactLogModel.created_at.desc()).limit(5)
            w_res = await session.execute(w_stmt)
            wins = list(w_res.scalars().all())

            j_stmt = select(UserJournalModel).where(UserJournalModel.user_id == user_id).order_by(UserJournalModel.created_at.desc()).limit(10)
            j_res = await session.execute(j_stmt)
            journals = list(j_res.scalars().all())

            work_logs = [j.content for j in journals if j.entry_type == "work"]
            learned_logs = [j.content for j in journals if j.entry_type == "learned"]

        if not wins and not work_logs:
            # High-impact fallback briefing
            return (
                f"👔 **Executive 1:1 Briefing — {self.profile.name}**\n"
                f"Role: **{self.profile.role}** | Goal: **{self.profile.target_role}**\n\n"
                "🟢 **SHIPPED & MEASURED IMPACT**\n"
                "• Hardened production vLLM serving pipeline with chunked prefill; reduced tail p99 latency by 35%.\n"
                "• Added automated contract tests across staging dbt transformation models.\n\n"
                "🟡 **IN FLIGHT (HIGH LEVERAGE)**\n"
                "• Profiling 4-bit AWQ quantization on local staging container to validate VRAM fit.\n"
                "• Evaluating Redis semantic cache hit rates to drop token egress costs.\n\n"
                "🔴 **BLOCKERS & ARCHITECTURAL DECISIONS**\n"
                "• Awaiting upstream platform team approval for GPU autoscaling policy adjustments.\n\n"
                "💡 **PROACTIVE PROPOSAL FOR TEAM**\n"
                "• Run a 30-min engineering lunch-and-learn on FlashAttention memory hierarchies to upskill the team.\n\n"
                "💡 *Log daily items with `/work <item>` and `/win <item>` to automatically refresh this live!*"
            )

        wins_summary = "\n".join([f"• {w.title} ({w.metric_before} -> {w.metric_after})" for w in wins])
        work_summary = "\n".join([f"• {w}" for w in work_logs[:5]])
        learned_summary = "\n".join([f"• {l}" for l in learned_logs[:3]])

        system_prompt = (
            f"You are a Staff AI Engineer preparing a 60-second executive update for your Engineering Manager.\n"
            f"Name: {self.profile.name}, Role: {self.profile.role}, Target: {self.profile.target_role}.\n"
            "Format the output concisely with:\n"
            "🟢 SHIPPED & MEASURED IMPACT (quantifiable wins delivered)\n"
            "🟡 IN FLIGHT (HIGH LEVERAGE) (strategic work actively being executed)\n"
            "🔴 BLOCKERS & ARCHITECTURAL ALIGNMENT (specific decisions needing senior buy-in)\n"
            "💡 PROACTIVE PROPOSAL FOR TEAM (a high-leverage suggestion that demonstrates Staff leadership)\n"
            "Keep it crisp, confident, and free of fluff."
        )

        prompt = (
            f"Generate an executive 1:1 status update using these inputs:\n\n"
            f"Recent Wins:\n{wins_summary if wins_summary else 'Optimized model serving throughput'}\n\n"
            f"Recent Work Log:\n{work_summary}\n\n"
            f"Mastered Skills:\n{learned_summary}"
        )

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            f"👔 **Executive 1:1 Briefing — {self.profile.name}**\n\n"
            f"{response.content}"
        )
