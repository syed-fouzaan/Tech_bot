"""Principal Architecture & Code Reviewer ('Architecture Roast').

Reviews pipelines, system designs, and code snippets through the eyes of an
uncompromising Principal Engineer, detailing scale failure points, compute waste,
and drop-in refactors.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class ArchitectureReviewer:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def review_architecture(self, architecture_text: str) -> str:
        """
        Reviews an architecture description or code snippet.
        """
        if not architecture_text.strip():
            return (
                "⚔️ **Principal Architecture & Code Review ('Roast')**\n\n"
                "Paste your pipeline design, system architecture, SQL model, or Python code:\n"
                "Usage: `/review_arch <architecture description or code snippet>`\n\n"
                "Example:\n"
                "`/review_arch FastAPI endpoint loading LLaMA-3 with torch.no_grad() and doing batch inference synchronously on request`"
            )

        system_prompt = (
            f"You are an uncompromising Principal AI & Data Infrastructure Architect advising a Senior Engineer.\n"
            f"Context: Local hardware is {self.profile.hardware.get('local_gpu')}; target role is {self.profile.target_role}.\n"
            "Review the submitted architecture or code snippet with brutal technical precision. Structure your output with:\n"
            "1. 💥 WHERE IT BREAKS AT 10x SCALE (concurrency bottlenecks, memory fragmentation, worker deadlocks, OOM spikes)\n"
            "2. 💸 RESOURCE & COMPUTE INEFFICIENCIES (unbatched GPU copies, redundant serialization, blocking I/O, cache misses)\n"
            "3. ⚡ 3 CONCRETE PRINCIPAL-LEVEL REFACTORS (step-by-step structural remedies)\n"
            "4. 🛠️ DROP-IN PRODUCTION CODE REFACTOR (minimal, working, hardened snippet)\n"
            "Be direct, technically rigorous, and avoid generic fluff."
        )

        prompt = f"Perform a Principal-level architecture & scalability review of the following:\n\n{architecture_text}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
