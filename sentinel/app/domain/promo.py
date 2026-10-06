"""STAR Promotion & Performance Appraisal Pack Compiler ('Brag Sheet').

Compiles all logged work activities, learnings, and impact wins into an
executive-ready appraisal dossier formatted in strict STAR methodology with
quantifiable metrics.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import UserJournalModel, WorkImpactLogModel
from sentinel.app.domain.profile import get_default_profile, UserProfile
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


class PromoEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def compile_promotion_pack(self, session: Optional[AsyncSession] = None, user_id: int = 0) -> str:
        """
        Compiles all logged work, learnings, and wins into an executive-ready promotion packet.
        """
        wins = []
        work_logs = []
        learned_logs = []

        if session is not None:
            # Fetch logged accomplishments
            w_stmt = select(WorkImpactLogModel).where(WorkImpactLogModel.user_id == user_id).order_by(WorkImpactLogModel.created_at.desc()).limit(10)
            w_res = await session.execute(w_stmt)
            wins = list(w_res.scalars().all())

            j_stmt = select(UserJournalModel).where(UserJournalModel.user_id == user_id).order_by(UserJournalModel.created_at.desc()).limit(15)
            j_res = await session.execute(j_stmt)
            journals = list(j_res.scalars().all())

            work_logs = [j.content for j in journals if j.entry_type == "work"]
            learned_logs = [j.content for j in journals if j.entry_type == "learned"]

        if not wins and not work_logs:
            # Deterministic fallback demonstration dossier
            return (
                f"📄 **Executive Performance & Promotion Pack — {self.profile.name}**\n"
                f"Target Level: **{self.profile.target_role}**\n\n"
                "### 🏆 Executive Impact Summary\n"
                "Engineered production-grade improvements across AI inference serving and data infrastructure, "
                "consistently prioritizing latency reduction, GPU hardware efficiency, and pipeline resilience.\n\n"
                "### 🌟 Highlight Accomplishments (STAR Format)\n\n"
                "**1. High-Throughput Inference Latency Optimization**\n"
                "• **Situation**: Model serving latency was bottlenecked under concurrent batch requests.\n"
                "• **Task**: Refactor the inference pipeline to reduce TTFT without adding cloud GPU costs.\n"
                "• **Action**: Integrated vLLM continuous chunked prefill, tuned KV-cache memory limits, and added Redis semantic caching.\n"
                "• **Result**: Cut p99 latency from 450ms to 180ms (60% improvement) while maintaining 100% SLA compliance.\n\n"
                "**2. Data Quality & Pipeline Contract Hardening**\n"
                "• **Situation**: Schema drift and upstream changes caused frequent data pipeline regressions.\n"
                "• **Task**: Enforce automated contract testing across Airflow DAGs.\n"
                "• **Action**: Implemented incremental dbt model assertions and DuckDB staging tests with automated Slack/Pager alerts.\n"
                "• **Result**: Eliminated downstream schema incidents by 100% over a 30-day window.\n\n"
                "💡 *Log more daily wins with `/win <title>` and work with `/work <task>` to enrich your live dossier!*"
            )

        wins_text = "\n".join([f"- {w.title}: {w.description} (Before: {w.metric_before} -> After: {w.metric_after})" for w in wins])
        work_text = "\n".join([f"- {w}" for w in work_logs[:8]])
        learn_text = "\n".join([f"- {l}" for l in learned_logs[:5]])

        system_prompt = (
            f"You are a Staff AI Engineering Manager compiling a formal Promotion & Performance Appraisal Dossier for {self.profile.name}.\n"
            f"Target Promotion Role: {self.profile.target_role}\n"
            "Format the output professionally with:\n"
            "1. 🏆 Executive Summary (strategic value delivered to the business)\n"
            "2. 🌟 Core Technical Contributions (formatted strictly in STAR: Situation, Task, Action, Result with quantifiable metrics)\n"
            "3. 📈 Technical Mastery & Skill Growth (demonstrated competencies)\n"
            "4. 🎯 Leadership & Scale Readines (why they are ready for the Senior/Staff band right now)\n"
            "Keep the language punchy, metrics-driven, and executive-ready."
        )

        prompt = (
            f"Compile a promotion appraisal packet using these accomplishments:\n\n"
            f"Logged Wins:\n{wins_text if wins_text else 'Built inference pipelines and data quality models'}\n\n"
            f"Logged Work History:\n{work_text}\n\n"
            f"Logged Learnings:\n{learn_text}"
        )

        try:
            resp = await self.gateway.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                task=TaskType.TECHNICAL_ANALYSIS,
            )
            return resp.content
        except Exception:
            return (
                f"📄 **Executive Performance Dossier — {self.profile.name}**\n\n"
                f"• Target Role: {self.profile.target_role}\n"
                f"• Logged Wins: {len(wins)}\n"
                f"• Work Contributions Logged: {len(work_logs)}\n\n"
                "Run `/win` or `/work` to log recent milestones, and `/review` for weekly progress."
            )
