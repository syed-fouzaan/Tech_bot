"""Hardware fit estimator: calculates VRAM, weights, and KV cache requirements."""

import re
from typing import Dict, Any, Optional
from pydantic import BaseModel


class HardwareFitResult(BaseModel):
    model_name: str
    param_count_b: float
    context_tokens: int
    user_vram_gb: float
    weights_fp16_gb: float
    weights_int8_gb: float
    weights_q4_gb: float
    kv_cache_gb: float
    verdict: str  # FITS_COMFORTABLY | FITS_IN_Q4 | NEEDS_MORE_VRAM
    explanation: str
    disclaimer: str = "ESTIMATE: Actual memory footprint depends on runtime engine (vLLM/llama.cpp) and CUDA overhead."


def parse_param_count(model_str: str) -> float:
    """Extracts parameter count in billions from model string (e.g. '7B', '14b', '70B', '3.8b')."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*[bB]", model_str)
    if match:
        return float(match.group(1))
    return 7.0  # default 7B if unspecified


def calculate_hardware_fit(
    model_str: str,
    user_vram_gb: float = 8.0,
    context_tokens: int = 4096,
) -> HardwareFitResult:
    """
    Formulas:
    weights_fp16_gb ≈ params_b * 2.0
    weights_int8_gb ≈ params_b * 1.0
    weights_q4_gb   ≈ params_b * 0.55
    kv_cache_gb     ≈ 2 * num_layers * hidden_size * ctx * 2 (approx ~0.15 GB per 1k context for 7B)
    """
    params_b = parse_param_count(model_str)
    weights_fp16 = round(params_b * 2.0, 1)
    weights_int8 = round(params_b * 1.0, 1)
    weights_q4 = round(params_b * 0.55, 1)

    # Approximated KV-cache scaling with context tokens
    kv_cache = round((params_b / 7.0) * (context_tokens / 1024.0) * 0.18, 2)
    cuda_overhead = 0.6  # typical CUDA runtime overhead in GB

    req_q4 = weights_q4 + kv_cache + cuda_overhead
    req_fp16 = weights_fp16 + kv_cache + cuda_overhead

    if user_vram_gb >= req_fp16:
        verdict = "FITS_COMFORTABLY"
        explanation = f"Model runs in FP16/BF16 natively on your {user_vram_gb} GB VRAM."
    elif user_vram_gb >= req_q4:
        verdict = "FITS_IN_Q4"
        explanation = f"Model fits comfortably under Q4/AWQ/GGUF quantization (requires ~{round(req_q4, 1)} GB VRAM)."
    else:
        verdict = "NEEDS_MORE_VRAM"
        explanation = (
            f"Model exceeds your {user_vram_gb} GB VRAM (needs ~{round(req_q4, 1)} GB even in Q4). "
            f"Use free cloud notebooks (Google Colab T4 / Kaggle 2xT4) or CPU offloading."
        )

    return HardwareFitResult(
        model_name=model_str,
        param_count_b=params_b,
        context_tokens=context_tokens,
        user_vram_gb=user_vram_gb,
        weights_fp16_gb=weights_fp16,
        weights_int8_gb=weights_int8,
        weights_q4_gb=weights_q4,
        kv_cache_gb=kv_cache,
        verdict=verdict,
        explanation=explanation,
    )
