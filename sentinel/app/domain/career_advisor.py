"""Personal Career & Skills Advisor Engine.

Analyzes what you worked on, what you learned, and your preferences to declare
your next learning milestones with real-world production scenarios.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel.app.models import UserJournalModel
from sentinel.app.domain.profile import get_default_profile, UserProfile
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


class CareerAdvisorEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def record_journal_entry(
        self,
        session: AsyncSession,
        user_id: int,
        entry_type: str,
        content: str,
        tags: Optional[str] = None,
    ) -> UserJournalModel:
        """Stores work, learning, or interest entry in the persistent database."""
        entry = UserJournalModel(
            user_id=user_id,
            entry_type=entry_type,
            content=content.strip(),
            tags=tags or "",
            created_at=datetime.now(timezone.utc),
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry

    async def get_recent_entries(
        self,
        session: AsyncSession,
        user_id: int,
        entry_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[UserJournalModel]:
        """Retrieves recent work/learning journal entries for a user."""
        stmt = select(UserJournalModel).where(UserJournalModel.user_id == user_id)
        if entry_type:
            stmt = stmt.where(UserJournalModel.entry_type == entry_type)
        stmt = stmt.order_by(UserJournalModel.created_at.desc()).limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def diagnose_career_path(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Diagnoses career progress based on logged work & learnings.
        Declares what the user MUST learn next with a concrete real-world example.
        """
        work_entries = await self.get_recent_entries(session, user_id, entry_type="work", limit=5)
        learn_entries = await self.get_recent_entries(session, user_id, entry_type="learned", limit=5)
        interest_entries = await self.get_recent_entries(session, user_id, entry_type="interest", limit=5)

        work_texts = [w.content for w in work_entries]
        learn_texts = [l.content for l in learn_entries]
        interests = [i.content for i in interest_entries] or self.profile.interests

        # If LLM is available, use it for rich synthesis
        prompt = (
            f"You are a Staff AI Systems Architect acting as a Personal Career Advisor.\n"
            f"User Target Role: {self.profile.target_role}\n"
            f"Current Stack: {', '.join(self.profile.work_context.stack)}\n"
            f"Local Hardware: {self.profile.hardware.get('local_gpu')}\n"
            f"Recent Work Logged: {work_texts if work_texts else 'Building data pipelines and inference endpoints'}\n"
            f"Recent Learnings Logged: {learn_texts if learn_texts else 'Transformer fundamentals and RAG'}\n"
            f"Key Interests: {interests}\n\n"
            "Produce an actionable advisory with:\n"
            "1. Verified Competencies (what they demonstrated)\n"
            "2. Critical Architectural Gaps (what's missing for Senior AI & Data Systems Engineer)\n"
            "3. DECLARED: What they MUST learn next (single highest-leverage topic)\n"
            "4. Real-World Production Example (a concrete system architecture scenario & practical implementation)\n"
        )

        try:
            resp = await self.gateway.generate(
                prompt=prompt,
                system_prompt="You are an uncompromising Staff AI Architect advising a rising Senior Engineer.",
                task=TaskType.TECHNICAL_ANALYSIS,
            )
            llm_text = resp.content
        except Exception:
            llm_text = None

        # Fallback deterministic analysis
        recent_all = " ".join(work_texts + learn_texts).lower()
        if "vllm" in recent_all or "inference" in recent_all:
            next_topic = "Continuous Chunked Prefill & Speculative Decoding"
            why_next = "You understand base serving; now you need p99 latency reduction and high-concurrency throughput optimization."
            example = (
                "Real-World Scenario: In an e-commerce assistant with 50+ concurrent users, speculative decoding "
                "uses a draft 1B model (Qwen-1.5B) to propose tokens to Llama-3-8B. Verification cuts TTFT by 45% "
                "without degrading generation quality."
            )
        elif "rag" in recent_all or "vector" in recent_all:
            next_topic = "Agentic Routing & RAG Evals with RAGAS / DeepEval"
            why_next = "Standard retrieval often hallucinates. Senior engineers must guarantee citation groundedness and context precision."
            example = (
                "Real-World Scenario: Implement a semantic cache with Redis and hybrid BM25 + dense ranking. "
                "Run a synthetic 50-question eval dataset to measure faithfulness before deploying to customer support."
            )
        elif "dbt" in recent_all or "airflow" in recent_all:
            next_topic = "Streaming / Micro-Batch Ingestion with Polars & DuckDB"
            why_next = "Batch DAGs are table stakes. Senior Data Engineers build near-real-time ingestion with zero warehouse compute waste."
            example = (
                "Real-World Scenario: Replace a 2-hour daily batch transform with a 15-minute incremental DuckDB "
                "pipeline processing Parquet files on S3 with schema evolution checks."
            )
        else:
            next_topic = "Model Quantization & Paged KV-Cache Memory Management"
            why_next = "Calibrated for your RTX 4060 (8GB VRAM); essential for self-hosting large models locally without OOM errors."
            example = (
                "Real-World Scenario: Quantize a 7B model using AutoAWQ 4-bit GEMM kernels. Profile VRAM allocation "
                "per sequence (16k context window) to prevent OOM spikes during batch inference."
            )

        return {
            "target_role": self.profile.target_role,
            "recent_work": work_texts[:3],
            "recent_learned": learn_texts[:3],
            "interests": interests[:4],
            "declared_next_topic": next_topic,
            "why_next": why_next,
            "real_world_example": example,
            "advisory_notes": llm_text,
        }
