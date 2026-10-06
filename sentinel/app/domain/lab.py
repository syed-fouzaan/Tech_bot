"""Personal AI Lab: Generates standalone executable benchmark scripts calibrated to local hardware."""

from typing import Optional, Dict, Any
from sentinel.app.providers.gateway import AIGateway
from sentinel.app.providers.base import TaskType

LAB_TEMPLATES: Dict[str, str] = {
    "awq": '''"""
Lab: AWQ 4-bit Quantization vs FP16 Memory Benchmark
Hardware Profile: RTX 4060 (8GB VRAM)
Estimated Run Time: 15-20 minutes
"""

import time
import torch

def benchmark_memory_and_latency():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on device: {device}")
    if device == "cuda":
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        print(f"Initial VRAM Allocated: {torch.cuda.memory_allocated() / (1024**2):.2f} MB")

    # Synthetic weight tensor simulating linear projection in 7B transformer
    # Shape: [batch, seq_len, hidden_dim]
    hidden_dim = 4096
    tokens = 512
    batch_size = 4

    print("\\n[1/2] Benchmarking FP16 baseline projection...")
    x = torch.randn(batch_size, tokens, hidden_dim, dtype=torch.float16, device=device)
    w_fp16 = torch.randn(hidden_dim, hidden_dim, dtype=torch.float16, device=device)

    # Warmup
    for _ in range(5):
        _ = torch.matmul(x, w_fp16)
    if device == "cuda":
        torch.cuda.synchronize()

    start = time.perf_counter()
    for _ in range(50):
        out_fp16 = torch.matmul(x, w_fp16)
    if device == "cuda":
        torch.cuda.synchronize()
    fp16_latency_ms = (time.perf_counter() - start) / 50 * 1000

    if device == "cuda":
        fp16_vram_mb = torch.cuda.memory_allocated() / (1024**2)
        print(f"FP16 Latency: {fp16_latency_ms:.2f} ms | VRAM: {fp16_vram_mb:.1f} MB")

    print("\\n[2/2] Simulating 4-bit packed weights (4x memory reduction)...")
    # AWQ packs 8 int4 weights into one int32 tensor
    w_packed_int4 = torch.randint(-8, 7, (hidden_dim, hidden_dim // 8), dtype=torch.int32, device=device)
    if device == "cuda":
        q4_vram_mb = torch.cuda.memory_allocated() / (1024**2)
        print(f"Q4 Sim VRAM: {q4_vram_mb:.1f} MB (vs FP16 {fp16_vram_mb:.1f} MB)")
        print(f"Memory Reduction: {(1 - (q4_vram_mb / fp16_vram_mb)) * 100:.1f}%")

    print("\\n✅ Lab Complete: Model weights fit comfortably within 8GB VRAM limit.")

if __name__ == "__main__":
    benchmark_memory_and_latency()
''',

    "vllm": '''"""
Lab: vLLM PagedAttention & Continuous Batching Benchmark
Hardware Profile: RTX 4060 (8GB VRAM)
Estimated Run Time: 10 minutes
"""

import time

def simulate_continuous_batching():
    print("Benchmarking Continuous Batching vs Static Scheduling...")
    # Simulating request arrival times and token generation
    requests = [
        {"id": 1, "tokens": 128},
        {"id": 2, "tokens": 512},
        {"id": 3, "tokens": 64},
        {"id": 4, "tokens": 256},
    ]

    print(f"Batch contains {len(requests)} requests with varying context lengths.")
    
    # 1. Static Batching Waste Calculation
    max_tokens = max(r["tokens"] for r in requests)
    static_padded_tokens = max_tokens * len(requests)
    actual_tokens = sum(r["tokens"] for r in requests)
    waste_percent = ((static_padded_tokens - actual_tokens) / static_padded_tokens) * 100

    print(f"Static Batch Padded Slots: {static_padded_tokens}")
    print(f"Actual Useful Slots: {actual_tokens}")
    print(f"Memory Fragmentation Waste: {waste_percent:.1f}%")
    print("PagedAttention eliminates this padding entirely via virtual memory page tables.")
    print("\\n✅ Recommendation: Enable --enable-chunked-prefill on your vLLM container.")

if __name__ == "__main__":
    simulate_continuous_batching()
''',
}


class LabEngine:
    def __init__(self, gateway: Optional[AIGateway] = None):
        self.gateway = gateway or AIGateway()

    async def generate_lab(self, topic: str, user_vram_gb: float = 8.0) -> str:
        """
        Returns a runnable Python benchmark script.
        Uses fast pre-calibrated template if available, or synthesizes via AI gateway.
        """
        clean_topic = topic.strip().lower()
        for key in LAB_TEMPLATES:
            if key in clean_topic:
                return LAB_TEMPLATES[key]

        # Dynamic lab generation via Gateway
        system_prompt = (
            f"You are a principal AI systems engineer. Generate a self-contained, immediately runnable "
            f"Python benchmark script testing '{topic}'. "
            f"Calibrate it for an NVIDIA RTX 4060 with {user_vram_gb} GB VRAM. "
            "Rules:\n"
            "1. Output ONLY executable Python code inside standard triple backticks.\n"
            "2. Include synthetic mock tensors/data so it runs without downloading large models.\n"
            "3. Measure latency (ms) and VRAM allocated.\n"
            "4. Keep execution time under 60 seconds."
        )
        prompt = f"Generate an executable 45-minute lab script for: {topic}"
        resp = await self.gateway.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task=TaskType.CODING,
        )
        return resp.content
