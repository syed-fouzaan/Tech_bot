"""Staff System Design Patterns Engine.

Delivers battle-tested architectural blueprints for distributed AI serving
and modern data engineering pipelines.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sentinel.app.domain.profile import get_default_profile, UserProfile


SYSTEM_PATTERNS = [
    {
        "id": "chunked_prefill",
        "title": "Continuous Chunked Prefill & PagedAttention",
        "domain": "LLM Inference Infrastructure",
        "problem": "Long input prompts starve decoding requests of compute, causing massive p99 Time-To-First-Token (TTFT) and inter-token latency spikes.",
        "solution": "Chunk incoming prefill tokens into uniform batches (e.g., 512 tokens) and co-schedule them alongside active decoding tokens in the same forward pass.",
        "tradeoff": "Increases overall GPU compute utilization to ~85%, but slightly increases individual single-request prefill latency.",
        "edge_case": "KV cache fragmentation when batch size fluctuates wildly; mitigated by PagedAttention virtual memory block tables.",
        "code_snippet": (
            "# vLLM Engine Configuration with Chunked Prefill\n"
            "from vllm import EngineArgs, LLMEngine\n\n"
            "engine_args = EngineArgs(\n"
            "    model='meta-llama/Meta-Llama-3.1-8B-Instruct',\n"
            "    enable_chunked_prefill=True,\n"
            "    max_num_batched_tokens=512,\n"
            "    gpu_memory_utilization=0.90,\n"
            ")\n"
            "engine = LLMEngine.from_engine_args(engine_args)"
        ),
    },
    {
        "id": "semantic_cache",
        "title": "Two-Tier Semantic Vector Caching with Cosine Distance Gate",
        "domain": "Cost-Optimization & RAG Serving",
        "problem": "80% of enterprise RAG queries are semantically redundant; querying an LLM repeatedly wastes thousands in cloud GPU compute.",
        "solution": "Embed incoming queries using a lightweight encoder (e.g. BGE-small) and perform an exact Redis/Qdrant vector similarity check against previous answered queries. Return cached answer if similarity > 0.94.",
        "tradeoff": "Sub-10ms cache hits for recurring queries; requires strict TTL eviction policies for data freshness.",
        "edge_case": "False positive hits on subtle prompt inversions (e.g., 'What is X?' vs 'What is NOT X?'); solved by hybrid keyword + negation checks.",
        "code_snippet": (
            "import redis\n"
            "import numpy as np\n\n"
            "def query_semantic_cache(redis_client, query_vector, threshold=0.94):\n"
            "    # Redis Vector Similarity Search (HNSW)\n"
            "    results = redis_client.ft('cache_idx').search(query_vector)\n"
            "    if results and results.docs[0].score >= threshold:\n"
            "        return results.docs[0].cached_response\n"
            "    return None"
        ),
    },
    {
        "id": "speculative_decoding",
        "title": "Speculative Decoding with Small Draft Verification",
        "domain": "Low-Latency LLM Serving",
        "problem": "Autoregressive generation is memory-bandwidth bound, generating only 1 token per full model forward pass.",
        "solution": "Use a small draft model (e.g., Llama-3-68M or 1B) to speculate K candidate tokens in rapid succession, then verify all K tokens concurrently in a single forward pass of the 8B/70B target model.",
        "tradeoff": "2x-3x speedup on token generation rate with zero quality degradation; requires additional VRAM for the draft model weights.",
        "edge_case": "Low acceptance rate on complex code or math tasks causing speculative rollback overhead.",
        "code_snippet": (
            "from transformers import AutoModelForCausalLM, AutoTokenizer\n\n"
            "target = AutoModelForCausalLM.from_pretrained('meta-llama/Meta-Llama-3.1-8B-Instruct', device_map='cuda')\n"
            "assistant = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.2-1B-Instruct', device_map='cuda')\n\n"
            "# Generates 2.4x faster via speculative verification\n"
            "outputs = target.generate(input_ids, assistant_model=assistant, max_new_tokens=100)"
        ),
    },
    {
        "id": "arrow_ipc",
        "title": "Zero-Copy Apache Arrow IPC Streaming",
        "domain": "High-Throughput Data Infrastructure",
        "problem": "Serializing pandas DataFrames into JSON or CSV across service boundaries bottlenecks data ingestion and doubles RAM usage.",
        "solution": "Transmit tabular record batches directly over Unix sockets or memory-mapped files via Apache Arrow IPC stream format without copying bytes into Python runtime memory.",
        "tradeoff": "Near-instantaneous cross-process transfer (10 GB/s throughput); requires both services to share Arrow schema.",
        "edge_case": "Endianness or memory alignment mismatches across distributed nodes.",
        "code_snippet": (
            "import pyarrow as pa\n"
            "import pyarrow.ipc as ipc\n\n"
            "def stream_batches(table: pa.Table, sink):\n"
            "    with ipc.new_stream(sink, table.schema) as writer:\n"
            "        writer.write_table(table)"
        ),
    },
]


class DesignPatternEngine:
    def __init__(self, profile: Optional[UserProfile] = None):
        self.profile = profile or get_default_profile()

    def get_pattern(self, pattern_id_or_name: Optional[str] = None) -> str:
        """Retrieves a specific or daily rotating architectural design pattern."""
        selected = None
        if pattern_id_or_name and pattern_id_or_name.strip():
            query = pattern_id_or_name.strip().lower()
            for p in SYSTEM_PATTERNS:
                if query in p["id"] or query in p["title"].lower() or query in p["domain"].lower():
                    selected = p
                    break

        if not selected:
            # Rotate by day of the year
            day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
            selected = SYSTEM_PATTERNS[day_of_year % len(SYSTEM_PATTERNS)]

        return (
            f"🏛️ **Staff System Design Pattern: {selected['title']}**\n"
            f"Domain: **{selected['domain']}**\n\n"
            f"🚨 **The Production Bottleneck**:\n{selected['problem']}\n\n"
            f"🧩 **Architectural Solution**:\n{selected['solution']}\n\n"
            f"⚖️ **Trade-Offs & Budget Impact**:\n{selected['tradeoff']}\n\n"
            f"⚠️ **Edge Case / Scale Failure Mode**:\n{selected['edge_case']}\n\n"
            f"💻 **Production Implementation Blueprint**:\n"
            f"```python\n{selected['code_snippet']}\n```\n"
            "💡 *Run `/pattern` daily for new blueprints or `/pattern <name>` to query specific patterns.*"
        )
