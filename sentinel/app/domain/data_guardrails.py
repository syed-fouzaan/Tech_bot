"""Data Quality Guardrails Generator.

Generates production Pandera, Pydantic v2, and Great Expectations schemas
to catch corrupted rows, null anomalies, and type drift in data pipelines
and reports before downstream consumers fail.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class DataGuardrailsEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def generate_guardrails(self, spec: str) -> str:
        """Generates schema validation rules and code for a data pipeline or report."""
        clean = spec.strip()
        if not clean:
            return (
                "🛡️ **Data Quality Guardrails Generator**\n\n"
                "Describe your dataset, report columns, or validation requirements:\n"
                "Usage: `/guardrails <columns or data description>`\n\n"
                "Examples:\n"
                "• `/guardrails Machine stoppages: timestamp, machine_id (int), duration_seconds (positive), reason_code (enum), shift (1, 2, 3)`\n"
                "• `/guardrails Tube Investment report: part_no (string), weight_kg (float > 0), scrap_count, inspection_date`\n"
                "• `/guardrails User embeddings: user_id (UUID), vector (list of float, length 1536), created_at`"
            )

        system_prompt = (
            "You are a Staff Data Quality & Governance Architect.\n"
            "Generate an airtight, production-grade schema validation guardrail suite based on the user's data specification.\n"
            "Provide:\n"
            "1. 🛡️ PANDERA DATAFRAME SCHEMA (Complete, executable Python code with Column checks, nullable constraints, and custom range validators)\n"
            "2. 📦 PYDANTIC V2 ROW MODEL (For stream ingestion / API request parsing with field validators)\n"
            "3. ⚠️ TOP 3 SILENT ANOMALIES PREVENTED (e.g. negative durations, timezone drift, duplicate primary keys)\n"
            "4. 🚀 DROP-IN PIPELINE INTEGRATION SNIPPET (How to filter and quarantine invalid rows cleanly into a dead-letter log without crashing the main batch job)\n"
            "Keep the code clean, modular, and directly copy-pasteable."
        )

        prompt = f"Generate production data quality guardrails and Pandera/Pydantic schemas for:\n\n{clean}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            "🛡️ **Production Data Quality Guardrails**\n\n"
            f"{response.content}"
        )
