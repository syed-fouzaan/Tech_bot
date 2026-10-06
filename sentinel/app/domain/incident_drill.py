"""Production Incident & Post-Mortem Drill Engine.

Simulates critical production outages across AI serving and data pipelines,
prompting the engineer for real-time triage steps, and evaluating Root Cause Analysis (RCA),
Mean Time to Detect (MTTD), and Mean Time to Remediate (MTTR).
"""

from typing import Optional, List, Dict, Any
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


INCIDENT_SCENARIOS = [
    {
        "title": "vLLM KV Cache Thrashing & OOM Cascade",
        "system": "Real-time LLM inference cluster (vLLM 0.5.4 + FastAPI)",
        "symptom": "p99 latency spiked from 180ms to 9.2s. 3 GPU worker nodes restarted with exit code 137 (OOM Killer). Queue backlog growing at 50 req/sec.",
        "clues": "Recent deployment increased max_model_len to 8192 without tuning gpu_memory_utilization. Heavy concurrent multi-turn user sessions.",
    },
    {
        "title": "Kafka Partition Rebalance Storm & Stream Consumer Lag",
        "system": "Embedding & Vector Ingestion Stream (Kafka + Ray Workers + Qdrant)",
        "symptom": "Consumer group lag exceeded 850,000 messages. Ray workers cycling in heartbeat timeout disconnects.",
        "clues": "Worker processing batch size spiked due to a batch of large PDF document embeddings taking 45s per chunk, exceeding max.poll.interval.ms.",
    },
    {
        "title": "DuckDB WAL Lock Contention on Concurrent Staging Pipeline",
        "system": "Airflow ETL + DuckDB in-memory staging + Parquet Lakehouse",
        "symptom": "DAG runs failing with 'Catalog Error: Could not acquire write lock' across 12 scheduled hourly runs.",
        "clues": "Two parallel DAGs were configured to write incrementally to the same staging .duckdb database file without external locking or separate read-only connections.",
    },
    {
        "title": "Silent Embedding Model Dimension Mismatch in Production RAG",
        "system": "Hybrid Search RAG Service (pgvector + BM25)",
        "symptom": "Search recall dropped to 8%. Customer query results returning completely irrelevant documents with 0.12 cosine similarity.",
        "clues": "Upstream embedding service silently switched from bge-large-en-v1.5 (1024 dims) to a newly deployed text-embedding-3-small (1536 dims) truncated or zero-padded.",
    },
]


class IncidentDrillEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def start_drill(self, scenario_index: Optional[int] = None) -> str:
        """Starts a live incident triage drill."""
        idx = scenario_index if scenario_index is not None and 0 <= scenario_index < len(INCIDENT_SCENARIOS) else 0
        sc = INCIDENT_SCENARIOS[idx]

        return (
            "🚨 **CRITICAL PRODUCTION INCIDENT DRILL — SEV-1 OUTAGE**\n\n"
            f"**Incident**: {sc['title']}\n"
            f"**Affected System**: {sc['system']}\n"
            f"**Observed Symptoms**: `{sc['symptom']}`\n\n"
            "🔍 **Initial Telemetry & Clues**:\n"
            f"• {sc['clues']}\n\n"
            "—"*24 + "\n"
            "🛠️ **YOUR MISSION (Staff On-Call Engineer)**:\n"
            "1. **Triage & Containment**: How do you stop bleeding immediately (under 2 minutes)?\n"
            "2. **Root Cause Analysis (RCA)**: What is the underlying architectural bug?\n"
            "3. **Permanent Prevention**: What safeguard/circuit-breaker prevents this forever?\n\n"
            "💡 *Reply with your mitigation plan*: `/drill solve <your triage and fix steps>`"
        )

    async def evaluate_drill(self, user_mitigation: str) -> str:
        """Evaluates engineer's incident response like a Principal Systems Reliability Architect."""
        if not user_mitigation.strip():
            return "Usage: `/drill solve <your step-by-step triage and mitigation actions>`"

        system_prompt = (
            "You are a Principal AI Infrastructure & SRE Architect grading an on-call engineer's "
            "incident triage and post-mortem response to a critical Sev-1 outage.\n"
            "Evaluate rigorously with:\n"
            "1. ⏱️ CONTAINMENT SPEED & ACCURACY (Did they stop customer impact first before debugging?)\n"
            "2. 🔬 ROOT CAUSE DEPTH (Did they identify the exact concurrency, memory, or network issue?)\n"
            "3. 🛡️ PERMANENT SAFEGUARDS (Did they add circuit breakers, health checks, or telemetry alerts?)\n"
            "4. 🎖️ ON-CALL GRADE: S-TIER (Principal) | A-TIER (Senior) | B-TIER (Junior) | RETRY (Caused secondary cascade)\n"
            "5. 💡 BATTLE-TESTED PRINCIPAL FIX (The exact production configuration or command to resolve it)."
        )

        prompt = f"Grade this incident triage plan for an AI/Data infrastructure outage:\n\n{user_mitigation}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
