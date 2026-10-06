"""Regex & Log Parser Synthesizer.

Converts messy industrial machine logs, stoppage scan outputs, and application
traces into clean, ultra-fast compiled Python regexes and Polars/DuckDB ingestion scripts.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class LogParserEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def parse_log_sample(self, log_sample: str) -> str:
        """Synthesizes high-speed regex and ingestion pipelines from log samples."""
        clean = log_sample.strip()
        if not clean:
            return (
                "📜 **Regex & Log Parser Synthesizer**\n\n"
                "Paste 1-3 lines of raw logs or stoppage scan text to synthesize an ultra-fast parser:\n"
                "Usage: `/parse_log <raw log sample lines>`\n\n"
                "Examples:\n"
                "• `/parse_log 2026-10-06 14:22:01 [STOPPAGE] Machine=TI-04 Line=Tube2 Reason='Hydraulic Pressure Drop' Duration=340s`\n"
                "• `/parse_log [WARN] 2026-10-06T09:12:44.120Z vllm.engine - Queue backlog: 42 waiting requests, KV cache at 88%`"
            )

        system_prompt = (
            "You are a Principal Data Ingestion Engineer.\n"
            "Analyze the provided log lines and generate a production-grade, high-throughput parsing pipeline.\n"
            "Structure your output:\n"
            "1. 🧩 OPTIMIZED COMPILED REGEX (With clean Python (?P<name>...) named capture groups and type mappings)\n"
            "2. ⚡ ULTRA-FAST INGESTION PIPELINE (Executable Python snippet using Polars, DuckDB, or Pandas parsing lines into a clean DataFrame)\n"
            "3. 🛡️ MALFORMED LINE HANDLING (Dead-letter quarantine logic so bad log lines never crash the parser)\n"
            "4. ⏱️ BENCHMARK THROUGHPUT (Expected parse rate in lines/sec using compiled regex)"
        )

        prompt = f"Synthesize an ultra-fast regex and structured data parser for these log lines:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            "📜 **Synthesized Log Parser & Ingestion Script**\n\n"
            f"{response.content}"
        )
