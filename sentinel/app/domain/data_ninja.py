"""Data Wrangling & SQL Ninja.

Synthesizes high-performance SQL, DuckDB, and Polars solutions for complex
data transformation problems (window functions, sessionization, flattening nested JSON).
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class DataNinjaEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def solve_transform(self, problem_description: str) -> str:
        """Solves a complex data transformation or SQL challenge."""
        clean = problem_description.strip()
        if not clean:
            return (
                "🥷 **Data Wrangling & SQL Ninja**\n\n"
                "Describe a tricky data transformation problem to get clean, high-performance code:\n"
                "Usage: `/data_ninja <problem description>` (or `/transform <problem>`)\n\n"
                "Examples:\n"
                "• `/data_ninja sessionize user clicks with 30-min inactivity gap in DuckDB`\n"
                "• `/data_ninja flatten deeply nested JSON array of objects with unnest in Postgres`\n"
                "• `/data_ninja compute 7-day rolling active users filling missing calendar dates in Polars`"
            )

        system_prompt = (
            "You are a Staff Data Engineer and SQL/Polars Specialist.\n"
            "Synthesize an elegant, ultra-fast solution for the user's data transformation problem.\n"
            "Structure your output as follows:\n"
            "1. 💡 THE CONCEPTUAL APPROACH (How to model it vectorially without Python loops: window frames, cumulative sums, unnesting)\n"
            "2. 🥷 HIGH-PERFORMANCE SOLUTION (Complete, runnable DuckDB / PostgreSQL / Polars snippet)\n"
            "3. ⚡ EDGE CASES HANDLED (NULL values, empty intervals, tie-breaking, performance scale)\n"
            "Keep the code clean, well-commented, and production-ready."
        )

        prompt = f"Solve this complex data transformation challenge:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            "🥷 **Data Ninja Solution**\n\n"
            f"{response.content}"
        )
