"""LLM Cost & Token Budget Calculator.

Calculates realistic monthly API token bills vs self-hosted GPU infrastructure
(vLLM on cloud instances or local hardware), KV cache memory limits,
and break-even query volumes.
"""

from typing import Optional, Dict, Any
import math


class CostCalculatorEngine:
    def __init__(self):
        # Pricing per 1M tokens (approximate market rates)
        self.api_prices = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
            "gemini-1-5-flash": {"input": 0.075, "output": 0.30},
            "deepseek-v3": {"input": 0.14, "output": 0.28},
        }

        # Cloud GPU monthly costs (on-demand 24/7)
        self.gpu_monthly_costs = {
            "aws_g5_xlarge_a10g": 735.0,     # 1x A10G (24GB VRAM) ~$1.006/hr
            "runpod_rtx_4090": 320.0,        # 1x RTX 4090 (24GB VRAM) ~$0.44/hr
            "local_rtx_4060": 0.0,           # User's local GPU ($0.00 infrastructure cost)
        }

    def calculate_cost(
        self,
        queries_per_day: int = 5000,
        avg_input_tokens: int = 1200,
        avg_output_tokens: int = 400,
        model_name: str = "gpt-4o-mini",
        cache_hit_rate: float = 0.30,
    ) -> str:
        """Calculates token costs, GPU hosting costs, and break-even points."""
        daily_input_m = (queries_per_day * avg_input_tokens) / 1_000_000
        daily_output_m = (queries_per_day * avg_output_tokens) / 1_000_000

        # Monthly (30 days)
        monthly_input_m = daily_input_m * 30
        monthly_output_m = daily_output_m * 30

        matched_model = "gpt-4o-mini"
        for k in self.api_prices:
            if k in model_name.lower():
                matched_model = k
                break

        prices = self.api_prices[matched_model]
        gross_monthly_cost = (monthly_input_m * prices["input"]) + (monthly_output_m * prices["output"])
        cached_monthly_cost = gross_monthly_cost * (1.0 - cache_hit_rate)
        cache_savings = gross_monthly_cost - cached_monthly_cost

        # GPU Self-hosted comparison
        runpod_4090 = self.gpu_monthly_costs["runpod_rtx_4090"]
        aws_a10g = self.gpu_monthly_costs["aws_g5_xlarge_a10g"]

        # KV Cache calculation for 8B model (e.g. Llama 3.1 8B in FP16 / FP8)
        # 2 * n_layers * n_heads * head_dim * seq_len * dtype_bytes
        # For Llama 3.1 8B: 32 layers, 8 kv heads (GQA), 128 head_dim, 2 bytes = ~128KB per token
        seq_len = avg_input_tokens + avg_output_tokens
        kv_cache_mb_per_req = (seq_len * 128 * 1024) / (1024 * 1024)

        return (
            f"💰 **LLM Cost & Token Budget Analysis: {matched_model}**\n\n"
            f"📈 **Workload Volume**:\n"
            f"• **Scale**: {queries_per_day:,} queries/day (~{queries_per_day * 30:,} queries/month)\n"
            f"• **Tokens**: {avg_input_tokens} input / {avg_output_tokens} output avg\n"
            f"• **Monthly Volume**: {monthly_input_m:.1f}M input + {monthly_output_m:.1f}M output tokens\n\n"
            "—"*24 + "\n"
            f"💸 **Cloud API Monthly Cost ({matched_model})**:\n"
            f"• Gross API Bill: **${gross_monthly_cost:,.2f} / month**\n"
            f"• With Semantic Cache ({int(cache_hit_rate*100)}% hits): **${cached_monthly_cost:,.2f} / month**\n"
            f"• 💡 Semantic Cache Savings: **${cache_savings:,.2f} / month**\n\n"
            "—"*24 + "\n"
            f"🖥️ **Self-Hosted GPU Serving (vLLM Open-Weight Model)**:\n"
            f"• **Local RTX 4060 (8GB)**: **$0.00 / month** (Free development & batch testing!)\n"
            f"• **RunPod RTX 4090 (24GB)**: **${runpod_4090:,.2f} / month**\n"
            f"• **AWS g5.xlarge A10G (24GB)**: **${aws_a10g:,.2f} / month**\n\n"
            "⚖️ **Break-Even Analysis**:\n"
            f"{'• Self-hosting is CHEAPER than API calls at this volume!' if cached_monthly_cost > runpod_4090 else '• Managed API is currently CHEAPER than dedicated 24/7 cloud GPU hosting.'}\n\n"
            f"🧠 **KV Cache Memory Footprint**:\n"
            f"• ~{kv_cache_mb_per_req:.1f} MB VRAM per active concurrent request (Llama-3.1-8B GQA).\n"
            f"• 10 concurrent requests = ~{kv_cache_mb_per_req * 10 / 1024:.2f} GB KV Cache VRAM."
        )

    def parse_and_calculate(self, args: str) -> str:
        """Parses arguments like '/calc_cost 10000 gpt-4o' or '/calc_cost'."""
        if not args.strip():
            return (
                "💰 **LLM Cost & Token Budget Calculator**\n\n"
                "Calculate API vs Self-Hosted GPU costs with semantic caching savings:\n"
                "Usage: `/calc_cost [queries_per_day] [model_name]`\n\n"
                "Examples:\n"
                "• `/calc_cost` — Standard benchmark (5,000 queries/day on gpt-4o-mini)\n"
                "• `/calc_cost 20000 gpt-4o` — High-scale analysis\n"
                "• `/calc_cost 10000 claude-3-5-sonnet` — Claude token budget"
            )

        parts = args.strip().split()
        qpd = 5000
        model = "gpt-4o-mini"

        for p in parts:
            if p.isdigit():
                qpd = int(p)
            elif any(m in p.lower() for m in self.api_prices.keys()):
                model = p.lower()

        return self.calculate_cost(queries_per_day=qpd, model_name=model)
