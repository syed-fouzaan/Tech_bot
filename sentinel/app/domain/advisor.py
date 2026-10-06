"""Implementation Advisor, 'Why Should I Care?', and Paper-to-Engineering translator."""

from typing import Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


class AdvisorEngine:
    def __init__(self, gateway: Optional[AIGateway] = None):
        self.gateway = gateway or AIGateway()

    async def get_implementation_guide(self, technology: str) -> str:
        """
        Generates actionable implementation blueprint with $0 path, local test, and production architecture.
        """
        system_prompt = (
            "You are a lead AI & Data infrastructure engineer. Provide an implementation guide for the requested technology. "
            "Must include:\n"
            "1. Overview & Problem Solved\n"
            "2. $0 Free / Local Setup Path (using Docker or Ollama/HuggingFace)\n"
            "3. Production Architecture & Dependencies (exact pinned package names)\n"
            "4. Minimal Runnable Code Sample\n"
            "5. What Breaks at Scale (bottlenecks, memory limits, edge cases)\n"
            "6. Recommended 45-minute experiment."
        )
        prompt = f"Provide an implementation guide for: {technology}"
        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.CODING,
        )
        return response.content

    async def analyze_why_it_matters(self, topic: str) -> str:
        """
        Analyzes a technology or announcement using the 10-point decision framework.
        """
        system_prompt = (
            "You are an AI engineering chief of staff. Answer clearly:\n"
            "1. What happened?\n"
            "2. What problem existed before?\n"
            "3. What actually changed?\n"
            "4. Who benefits vs. Who should ignore it?\n"
            "5. Production maturity level\n"
            "6. Decision: Act now, learn later, or ignore?"
        )
        prompt = f"Analyze why an AI engineer should care about: {topic}"
        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content

    async def translate_paper(self, paper_ref: str) -> str:
        """
        Translates academic paper into pragmatic engineering reality.
        """
        system_prompt = (
            "Translate this research paper into practical software engineering reality:\n"
            "- Core Insight (in simple English)\n"
            "- Previous approach vs Proposed approach\n"
            "- Verified benchmarks (do not fabricate numbers)\n"
            "- Implementation complexity (Small / Medium / Large)\n"
            "- Verdict: LEARN NOW | LEARN LATER | WATCH | IGNORE\n"
            "- Weekend 'Prove it' mini-project idea."
        )
        prompt = f"Translate this paper: {paper_ref}"
        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.TECHNICAL_ANALYSIS,
        )
        return response.content
