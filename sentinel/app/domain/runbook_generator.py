"""Production On-Call Runbook Generator.

Generates production incident runbooks, health check commands,
alert thresholds, and emergency recovery checklists for AI and data services.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


DEFAULT_RUNBOOKS = {
    "vllm": (
        "📋 **Production On-Call Runbook: vLLM Inference Service**\n\n"
        "### 🚨 Golden Signals & Alert Thresholds\n"
        "• **p99 Latency**: Alert if p99 > 800ms sustained over 3 mins.\n"
        "• **GPU Memory Saturation**: Alert if VRAM usage > 95% (Risk of CUDA OOM 137 exit).\n"
        "• **Queue Backlog**: Alert if pending request queue > 50 requests.\n\n"
        "### 🩺 Live Health Check & Telemetry\n"
        "• Liveness probe: `curl http://localhost:8000/health` (Expect 200 OK)\n"
        "• Prometheus metrics: `curl http://localhost:8000/metrics | grep vllm:num_requests_waiting`\n\n"
        "### 🩹 Emergency Mitigation & Restart Commands\n"
        "1. Drain traffic in reverse-proxy: `nginx -s reload` (drop upstream traffic)\n"
        "2. Soft restart workers: `kill -HUP <vllm_pid>`\n"
        "3. Clear stuck CUDA memory cache: `fuser -v /dev/nvidia* -k`\n"
        "4. Safe restart with conservative memory: `python -m vllm.entrypoints.openai.api_server --gpu-memory-utilization 0.85 --max-model-len 4096`\n\n"
        "### 🔄 Rollback Procedure\n"
        "• Rollback model container to previous verified image tag.\n"
        "• Verify fallback responses on staging port before re-enabling ingress traffic."
    ),
    "airflow": (
        "📋 **Production On-Call Runbook: Apache Airflow & Data Pipelines**\n\n"
        "### 🚨 Golden Signals & Alert Thresholds\n"
        "• **Scheduler Heartbeat**: Alert if heartbeat age > 60s.\n"
        "• **Task Queue Latency**: Alert if queued tasks > 25 tasks for > 5 mins.\n"
        "• **SLA Misses**: Alert immediately on any critical Gold-tier table DAG failure.\n\n"
        "### 🩺 Live Health Check\n"
        "• CLI diagnosis: `airflow jobs check --job-type SchedulerJob`\n"
        "• Unstick zombie tasks: `airflow tasks clear -s <dag_id> --yes`\n\n"
        "### 🩹 Emergency Mitigation\n"
        "1. Kill stuck worker processes: `pkill -f 'airflow celery worker'`\n"
        "2. Flush redis/rabbitmq queue: `redis-cli flushdb` (Caution: only for non-persistent queues)\n"
        "3. Restart scheduler cleanly: `airflow scheduler --daemon`\n\n"
        "### 🔄 Rollback Procedure\n"
        "• Revert git commit on DAGs repository; wait for Airflow DAG processor loop (default 30s)."
    ),
}


class RunbookEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def generate_runbook(self, service_name: str) -> str:
        """Emits a production on-call runbook for a specified service."""
        clean = service_name.strip().lower()
        if not clean:
            return (
                "📋 **Production On-Call Runbook Generator**\n\n"
                "Generate an emergency runbook with golden signals, health checks, and recovery commands:\n"
                "Usage: `/runbook <service_name>`\n\n"
                "Examples:\n"
                "• `/runbook vllm` — LLM serving cluster runbook\n"
                "• `/runbook airflow` — Data orchestration runbook\n"
                "• `/runbook kafka` — Streaming ingestion runbook\n"
                "• `/runbook duckdb` — Embedded analytical database runbook\n"
                "• `/runbook <any_custom_tech>` — AI-generated custom runbook"
            )

        if clean in DEFAULT_RUNBOOKS:
            return DEFAULT_RUNBOOKS[clean]

        system_prompt = (
            "You are a Principal Site Reliability & AI Infrastructure Architect.\n"
            "Create a strict, emergency on-call runbook for the requested service.\n"
            "Format the runbook with:\n"
            "1. 🚨 Golden Signals & Alert Thresholds (p99 latency, error rate %, resource saturation)\n"
            "2. 🩺 Health Check & Diagnostic Commands (curl, CLI queries, log inspection)\n"
            "3. 🩹 Immediate Mitigation & Emergency Restart Commands (concrete shell commands)\n"
            "4. 🔄 Safe Rollback Checklist (step-by-step to revert without data corruption)\n"
            "Keep it crisp, actionable, and formatted for high-pressure on-call debugging."
        )

        prompt = f"Generate an emergency on-call runbook for: {service_name}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            f"📋 **Production On-Call Runbook: {service_name.upper()}**\n\n"
            f"{response.content}"
        )
