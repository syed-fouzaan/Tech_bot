"""Deterministic Mock and Fallback Provider for offline runs and testing."""

import json
from typing import Any
from sentinel.app.providers.base import AIResponse, TaskType


class MockProvider:
    provider_id: str = "mock_deterministic"
    cost_class: str = "free"

    async def is_available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        task: TaskType = TaskType.CHAT,
        **kwargs: Any,
    ) -> AIResponse:
        # ponytail: deterministic rule-based output satisfies PRD requirements without burning tokens
        if task == TaskType.CLASSIFICATION:
            content = json.dumps({
                "category": "infrastructure",
                "importance_score": 0.85,
                "personal_relevance_score": 0.90,
                "priority": "MUST_KNOW",
                "reasoning": "Directly impacts inference optimization and production serving."
            })
        elif task == TaskType.COMPARISON:
            content = (
                "### Model Comparison Analysis\n"
                "- Architecture: Dense Decoder-only Transformer\n"
                "- Parameters: 7B (Reported)\n"
                "- Context Window: 128k tokens\n"
                "- License: Apache 2.0 (Permissive)\n"
                "- Production Feasibility: High via vLLM / Ollama\n"
                "- Benchmark: GSM8K 84.2%, HumanEval 72.1% (Source: Model Card, 2026)\n"
                "- Decision: Pick Model A for low-latency batch jobs, Model B for multi-turn tool calling."
            )
        elif task == TaskType.TECHNICAL_ANALYSIS:
            content = (
                "### Technical Breakdown\n"
                "**What Happened**: Major performance enhancement in KV-cache memory management.\n"
                "**Why It Matters**: Cuts GPU VRAM footprint by 35% during continuous batching.\n"
                "**What Changed**: Introduced PagedAttention v3 with speculative scheduling.\n"
                "**Recommended Action**: Deploy test container and benchmark on batch pipeline."
            )
        elif task == TaskType.FINAL_DIGEST:
            content = (
                "☀️ AI ENGINEERING BRIEF\n\n"
                "🔥 MUST KNOW\n"
                "1. vLLM Release: 35% VRAM Reduction in KV-Cache [✅ Verified]\n"
                "   Why you: Directly reduces inference cluster operating costs.\n"
                "   Do: Benchmark upgrade on staging container.\n\n"
                "⚡ SHOULD KNOW\n"
                "2. Qwen-2.5-Coder: Apache 2.0 weights published [✅ Verified]\n\n"
                "🏢 FOR YOUR WORK\n"
                "- Airflow 2.10 Released: enhanced task execution timeouts.\n\n"
                "🧠 TODAY'S LEARNING PRIORITY\n"
                "- Quantization fundamentals: AWQ vs GPTQ memory trade-offs.\n\n"
                "💻 PRACTICAL ACTION\n"
                "- Benchmark 4-bit quantization on a sample model."
            )
        else:
            content = f"Analysis completed for task '{task.value}'. Key insights verified against source evidence."

        return AIResponse(
            content=content,
            provider=self.provider_id,
            model="mock-v1",
            tokens_in=len(prompt) // 4,
            tokens_out=len(content) // 4,
            latency_ms=5.0,
            is_fallback=True,
        )
