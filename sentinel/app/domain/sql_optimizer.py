"""Slow SQL & Pipeline Optimizer.

Analyzes SQL queries, dbt models, and data pipelines for execution plan
bottlenecks (full table scans, unpushed predicates, Cartesian joins) and
emits optimized, production-hardened queries with indexing strategies.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class SQLOptimizerEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def optimize(self, query_or_code: str) -> str:
        """Analyzes and optimizes a SQL query or data pipeline snippet."""
        clean = query_or_code.strip()
        if not clean:
            return (
                "⚡ **Slow SQL & Pipeline Optimizer**\n\n"
                "Paste your slow SQL query, dbt model, or data pipeline snippet:\n"
                "Usage: `/optimize_sql <sql query or transformation>`\n\n"
                "Analyzes:\n"
                "• 🛑 Missing indexes, unpushed filter predicates, full scans\n"
                "• 💥 Cartesian joins & explosive fan-outs\n"
                "• 🚀 Window function & CTE materialization optimizations\n"
                "• 🛠️ Tailored for DuckDB, PostgreSQL, Snowflake, and BigQuery"
            )

        system_prompt = (
            "You are a Principal Database & Data Infrastructure Performance Architect.\n"
            "Analyze the submitted SQL query or data transformation with meticulous technical rigor.\n"
            "Structure your response:\n"
            "1. 🔍 THE PERFORMANCE BOTTLENECK (Explain why this query is slow or memory-hungry: lack of predicate pushdown, accidental cross joins, CTE materialization fences)\n"
            "2. ⚡ OPTIMIZED PRODUCTION REWRITE (Provide the fully rewritten, high-speed SQL query)\n"
            "3. 📊 INDEXING & PARTITION STRATEGY (Exact CREATE INDEX or PARTITION BY statements to optimize it)\n"
            "4. ⏱️ ESTIMATED SPEEDUP (e.g. 5x - 50x depending on table cardinality)"
        )

        prompt = f"Optimize this slow SQL query or data pipeline transformation:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
