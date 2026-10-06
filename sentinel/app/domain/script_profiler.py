"""Python Pipeline & Memory Leak Hunter.

Analyzes data pipelines, batch report generators, and Python scripts for:
- Quadratic memory bloat (e.g. pd.concat / list append in loops)
- Cell-by-cell Excel / openpyxl / xlsxwriter bottlenecks
- Unclosed file descriptors, DB connections, or thread leaks
- High-concurrency async blocking loops
Emits drop-in, memory-efficient vectorized rewrites with 10x-50x speedups.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class ScriptProfilerEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def profile_code(self, code_snippet: str) -> str:
        """Analyzes a Python script or loop for memory bloat and execution bottlenecks."""
        clean = code_snippet.strip()
        if not clean:
            return (
                "🔬 **Python Pipeline & Memory Leak Hunter**\n\n"
                "Paste your Python script, batch report loop, or data processing snippet:\n"
                "Usage: `/profile_script <python code snippet>` (or `/debug_code <code>`)\n\n"
                "Scans for:\n"
                "• 💥 Quadratic memory accumulation (`pd.concat` or `df.append` inside loops)\n"
                "• 🐌 Slow openpyxl / xlsxwriter cell iteration vs batch array dumping\n"
                "• 🔒 Leaked file descriptors, hanging database connections, and generator leaks\n"
                "• ⚡ Emits vectorized, chunked, production-hardened rewrites"
            )

        system_prompt = (
            "You are a Principal Python Performance Architect specializing in high-throughput data processing and reporting pipelines.\n"
            "Analyze the submitted Python code snippet with uncompromising technical precision.\n"
            "Structure your output:\n"
            "1. 🛑 THE CRITICAL BOTTLENECK / MEMORY LEAK (Identify why this code consumes excessive RAM or runs slowly: iterative concatenation, cell-by-cell I/O, uncollected memory buffers)\n"
            "2. ⚡ DROP-IN HIGH-PERFORMANCE REWRITE (Provide the fully rewritten, memory-capped, vectorized or chunked Python code)\n"
            "3. 📊 COMPLEXITY & BENCHMARK GAINS (Memory footprint delta: e.g. O(N^2) -> O(1) streaming; CPU speedup: e.g. 10x - 40x)\n"
            "4. 💡 2 PRINCIPAL-LEVEL PRO-TIPS (e.g. arrow table conversions, generator streaming, memory-mapping)"
        )

        prompt = f"Profile and optimize this Python data processing script:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            "🔬 **Python Pipeline Profile & Optimization**\n\n"
            f"{response.content}"
        )
