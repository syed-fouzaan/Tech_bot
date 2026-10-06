"""Model Comparison Engine: evidence-grounded side-by-side analysis."""

from typing import List, Dict, Any, Optional
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType


class ComparisonEngine:
    def __init__(self, gateway: Optional[AIGateway] = None):
        self.gateway = gateway or AIGateway()

    async def compare_models(self, models: List[str], user_vram_gb: float = 8.0) -> str:
        """
        Produces an evidence-backed comparison table and decision guide.
        """
        if not models:
            return "Please specify models to compare, e.g. `/compare qwen2.5-7b llama-3.1-8b`"

        model_list_str = ", ".join(models)
        system_prompt = (
            "You are a principal AI systems engineer. Compare the provided models rigorously. "
            "Rule: If a benchmark or parameter is not officially reported or verified, state 'Not reported' or 'Unknown'. "
            "Never invent missing figures. Structure output with:\n"
            "1. Side-by-side specs (Architecture, Parameters, Context, License, Quantization, Deployment options)\n"
            "2. Verified Benchmark Evidence (with source and date or 'Not reported')\n"
            "3. Production Trade-offs (latency, memory footprint)\n"
            f"4. Decision Guide for an engineer with {user_vram_gb} GB VRAM."
        )
        prompt = f"Compare the following models: {model_list_str}."

        response = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.COMPARISON,
        )
        return response.content
