"""Staff PR & Git Diff Review Assistant.

Scans code diffs or snippets for subtle, high-severity defects:
- GPU memory leaks & CUDA graph leaks (missing .detach(), accumulating tensors)
- Async event loop blocks (blocking sync calls in async def, thread starvation)
- Vector DB & prompt injection vulnerabilities
- Schema & contract regressions in data pipelines
Emits production-ready GitHub PR review markdown with line comments.
"""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType
from sentinel.app.domain.profile import get_default_profile, UserProfile


class PRReviewerEngine:
    def __init__(self, gateway: Optional[AIGateway] = None, profile: Optional[UserProfile] = None):
        self.gateway = gateway or AIGateway()
        self.profile = profile or get_default_profile()

    async def review_diff(self, diff_text: str) -> str:
        """Reviews a code snippet or git diff like a Staff Engineer."""
        if not diff_text.strip():
            return (
                "🔍 **Staff PR & Git Diff Review Assistant**\n\n"
                "Paste your code snippet or git diff to run an automated Staff-level review:\n"
                "Usage: `/pr_review <git diff or code snippet>`\n\n"
                "Checks automatically:\n"
                "• ⚡ **GPU/Memory**: Accumulating PyTorch tensors, missing `.detach()`, CUDA OOM traps\n"
                "• 🔄 **Async Bottlenecks**: Blocking I/O inside `async def`, missing semaphore bounds\n"
                "• 🛡️ **Security**: Prompt injection, unescaped vector queries, API key exposure\n"
                "• 📊 **Data Contracts**: Unchecked schema drift and unindexed vector filters"
            )

        system_prompt = (
            "You are a Staff AI & Data Infrastructure Engineer conducting a strict GitHub Pull Request review.\n"
            "Analyze the provided code diff or snippet for subtle, insidious production bugs.\n"
            "Structure your review as follows:\n"
            "### 🚨 Blocking Issues (Must Fix Before Merge)\n"
            "(Identify memory leaks, event loop blocking calls, or security vulnerabilities)\n\n"
            "### ⚡ Performance & Compute Optimizations\n"
            "(GPU tensor lifecycle, batching improvements, indexing, query planning)\n\n"
            "### 💬 Ready-to-Paste GitHub Review Comments\n"
            "(Provide exact markdown block with suggested diffs using standard GitHub markdown syntax: ```suggestion ... ```)\n\n"
            "### 🏷️ Verdict: APPROVE | REQUEST_CHANGES | COMMENT"
        )

        prompt = f"Conduct a Staff-level PR code review on this snippet/diff:\n\n{diff_text}"

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
