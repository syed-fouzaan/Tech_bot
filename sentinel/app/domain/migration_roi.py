"""Tech Migration ROI & Anti-Hype Calculator.

Calculates realistic migration cost, compute savings, latency deltas,
and evaluates when NOT to migrate (anti-hype reality check / YAGNI).
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class MigrationROIEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def calculate_roi(self, query: str) -> str:
        """Calculates migration ROI and anti-hype feasibility."""
        clean_query = query.strip()
        if not clean_query:
            return (
                "⚖️ **Tech Migration ROI & Anti-Hype Calculator**\n\n"
                "Compare migrating from your current technology to a newer alternative:\n"
                "Usage: `/roi <current_tech> vs <target_tech>` (or `/migrate <techA> <techB>`)\n\n"
                "Popular Examples:\n"
                "• `/roi Pandas vs Polars`\n"
                "• `/roi TGI vs vLLM`\n"
                "• `/roi Postgres-pgvector vs Qdrant`\n"
                "• `/roi Celery vs Ray`\n"
                "• `/roi FastAPI vs LitServe`"
            )

        system_prompt = (
            f"You are a Staff AI Infrastructure Architect advising an engineering team.\n"
            f"Hardware profile: {self.profile.hardware.get('local_gpu')}; Company context: {self.profile.work_context.domain}.\n"
            "Evaluate this tech stack migration with uncompromising fiscal and engineering realism. Structure your response:\n\n"
            "1. 📊 ESTIMATED LATENCY & THROUGHPUT DELTA (p50/p99 latency, RAM/VRAM footprint delta, concurrency limits)\n"
            "2. 💰 CLOUD & HARDWARE SAVINGS ($ saved per month at typical mid-market scale)\n"
            "3. 🛠️ REAL MIGRATION FRICTION (Engineering person-days, breaking API changes, rewrite surface area)\n"
            "4. 🛑 THE ANTI-HYPE REALITY CHECK (When you should NOT migrate; why sticking with the current tech might be smarter)\n"
            "5. 🏁 STAFF VERDICT: MIGRATE NOW | BENCHMARK ON STAGING FIRST | DO NOT MIGRATE (YAGNI)"
        )

        prompt = f"Calculate the full migration ROI, technical trade-offs, and anti-hype reality check for:\n\n{clean_query}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
