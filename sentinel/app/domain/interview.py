"""Mock Senior/Staff System Design Interviewer.

Generates real-world system design interview questions tailored for Senior AI & Data
Engineers and evaluates candidate solutions with strict Staff-level rubrics.
"""

from typing import Optional, List
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


INTERVIEW_TOPICS = [
    "Design a Real-Time High-Throughput vLLM Inference Service with 200ms p99 SLA",
    "Design a Scalable Multimodal RAG Engine for 5 Million Documents with Hybrid Search",
    "Design a Distributed Feature Store & Stream Ingestion Pipeline with DuckDB/Parquet",
    "Design an Agentic Tool-Calling Workflow with Self-Healing Error Recovery and State Persistence",
    "Design an In-Memory Quantization Serving Pipeline on Constrained Edge GPUs",
]


class InterviewEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def get_interview_scenario(self, topic: Optional[str] = None) -> str:
        """Generates a comprehensive system design challenge with strict constraints."""
        chosen_topic = topic.strip() if topic and topic.strip() else INTERVIEW_TOPICS[0]

        system_prompt = (
            "You are a Staff AI Systems Architect conducting a Senior/Staff System Design Interview. "
            "Formulate an uncompromising, real-world system design prompt. Include:\n"
            "1. 🎯 Problem Statement & Target Scale (QPS, latency p99 budget, data volume)\n"
            "2. 🛑 Hard Invariants & Constraints (GPU memory budget, zero data loss, cost caps)\n"
            "3. 📝 3 Key Architectural Questions the candidate must answer (Storage/Serving layer, Caching/Batching strategy, Failure recovery)\n"
            "Keep it crisp, challenging, and production-grounded."
        )

        prompt = f"Create a Staff-level system design interview problem for: {chosen_topic}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return (
            f"🎯 **Mock Staff System Design Interview**\n\n"
            f"{response.content}\n\n"
            "💡 *Reply with your architectural solution (components, data flow, trade-offs), and I will grade it against Staff-level rubrics!*"
        )

    async def evaluate_solution(self, user_solution: str) -> str:
        """Evaluates candidate's system design solution against Staff-level standards."""
        system_prompt = (
            "You are a Principal AI Systems Architect grading a Senior Engineer's System Design Interview response. "
            "Grade strictly on:\n"
            "1. 📊 Scalability & Latency (Did they handle p99 tail latency and batching?)\n"
            "2. 🛡️ Fault Tolerance & Edge Cases (What happens when a worker/GPU dies?)\n"
            "3. 💰 Cost & Compute Efficiency (Are they wasting VRAM or cloud dollars?)\n"
            "4. 🏆 Final Verdict: STRONG HIRE | HIRE | LEAN HIRE | NO HIRE\n"
            "5. 🚀 2 Principal-Level Improvements to elevate this solution."
        )

        prompt = f"Evaluate this system design response:\n\n{user_solution}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
