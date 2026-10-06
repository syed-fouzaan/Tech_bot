"""Dual-track living roadmap for AI and Data Engineering."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RoadmapNode(BaseModel):
    node_id: str
    track: str  # AI or DATA
    title: str
    difficulty: str  # Beginner, Intermediate, Advanced
    prerequisites: List[str] = Field(default_factory=list)
    estimated_hours: int
    theory_confidence: float = 0.0
    practice_confidence: float = 0.0
    production_confidence: float = 0.0
    prove_it_artifact: str
    status: str = "pending"  # pending, in_progress, completed


DEFAULT_ROADMAP_NODES: List[RoadmapNode] = [
    # AI Track
    RoadmapNode(
        node_id="ai_foundations",
        track="AI",
        title="ML & Deep Learning Foundations (PyTorch, backprop, autograd)",
        difficulty="Beginner",
        estimated_hours=10,
        theory_confidence=0.9,
        practice_confidence=0.85,
        production_confidence=0.7,
        prove_it_artifact="Self-implemented MLP and CNN from scratch in PyTorch",
        status="completed",
    ),
    RoadmapNode(
        node_id="ai_transformers",
        track="AI",
        title="Transformer Architecture & Attention Mechanisms",
        difficulty="Intermediate",
        prerequisites=["ai_foundations"],
        estimated_hours=12,
        theory_confidence=0.85,
        practice_confidence=0.8,
        production_confidence=0.7,
        prove_it_artifact="Multi-head self-attention module with causal masking",
        status="completed",
    ),
    RoadmapNode(
        node_id="ai_rag",
        track="AI",
        title="Production RAG: Chunking, Hybrid Search, Vector Stores & Evals",
        difficulty="Intermediate",
        prerequisites=["ai_transformers"],
        estimated_hours=15,
        theory_confidence=0.8,
        practice_confidence=0.75,
        production_confidence=0.6,
        prove_it_artifact="Hybrid search RAG pipeline evaluated using RAGAS",
        status="in_progress",
    ),
    RoadmapNode(
        node_id="ai_agents_mcp",
        track="AI",
        title="Agentic Systems & MCP Protocol (LangGraph, tool calling, state)",
        difficulty="Intermediate",
        prerequisites=["ai_rag"],
        estimated_hours=15,
        theory_confidence=0.75,
        practice_confidence=0.7,
        production_confidence=0.5,
        prove_it_artifact="Multi-step agent using LangGraph and Model Context Protocol",
        status="in_progress",
    ),
    RoadmapNode(
        node_id="ai_inference_vllm",
        track="AI",
        title="Inference Optimization: vLLM, PagedAttention & Continuous Batching",
        difficulty="Advanced",
        prerequisites=["ai_transformers"],
        estimated_hours=20,
        theory_confidence=0.7,
        practice_confidence=0.6,
        production_confidence=0.4,
        prove_it_artifact="Dockerized vLLM benchmark showing throughput vs latency curves",
        status="pending",
    ),
    RoadmapNode(
        node_id="ai_quantization",
        track="AI",
        title="Model Quantization: AWQ, GPTQ, GGUF & Hardware Constraints",
        difficulty="Advanced",
        prerequisites=["ai_inference_vllm"],
        estimated_hours=16,
        theory_confidence=0.6,
        practice_confidence=0.5,
        production_confidence=0.3,
        prove_it_artifact="Quantized model serving lab comparing perplexity and memory",
        status="pending",
    ),
    # Data Engineering Track
    RoadmapNode(
        node_id="data_sql_modeling",
        track="DATA",
        title="Advanced SQL & Dimensional Modeling (Kimball, Medallion)",
        difficulty="Beginner",
        estimated_hours=12,
        theory_confidence=0.9,
        practice_confidence=0.85,
        production_confidence=0.8,
        prove_it_artifact="Analytics schema modeled in bronze/silver/gold layers",
        status="completed",
    ),
    RoadmapNode(
        node_id="data_dbt_transformation",
        track="DATA",
        title="Transformations with dbt & Data Quality Testing",
        difficulty="Intermediate",
        prerequisites=["data_sql_modeling"],
        estimated_hours=14,
        theory_confidence=0.8,
        practice_confidence=0.75,
        production_confidence=0.6,
        prove_it_artifact="dbt project with schema tests, freshness checks, and documentation",
        status="in_progress",
    ),
    RoadmapNode(
        node_id="data_orchestration",
        track="DATA",
        title="Pipeline Orchestration (Apache Airflow / Dagster)",
        difficulty="Intermediate",
        prerequisites=["data_dbt_transformation"],
        estimated_hours=18,
        theory_confidence=0.75,
        practice_confidence=0.7,
        production_confidence=0.5,
        prove_it_artifact="Production Airflow DAG with retries, alerts, and SLAs",
        status="in_progress",
    ),
    RoadmapNode(
        node_id="data_lakehouse",
        track="DATA",
        title="Modern Lakehouse Formats: Parquet, Delta Lake & DuckDB",
        difficulty="Advanced",
        prerequisites=["data_orchestration"],
        estimated_hours=16,
        theory_confidence=0.6,
        practice_confidence=0.5,
        production_confidence=0.3,
        prove_it_artifact="DuckDB + Delta Lake pipeline benchmarked against row-based stores",
        status="pending",
    ),
]


class RoadmapEngine:
    def __init__(self, nodes: Optional[List[RoadmapNode]] = None):
        self.nodes = nodes or DEFAULT_ROADMAP_NODES

    def get_summary(self) -> Dict[str, Any]:
        total = len(self.nodes)
        completed = sum(1 for n in self.nodes if n.status == "completed")
        in_progress = sum(1 for n in self.nodes if n.status == "in_progress")
        pending = sum(1 for n in self.nodes if n.status == "pending")

        return {
            "total_nodes": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "progress_percent": round((completed / total) * 100, 1) if total else 0,
            "nodes": [n.model_dump() for n in self.nodes],
        }

    def get_next_recommended_nodes(self, count: int = 2) -> List[RoadmapNode]:
        """Returns pending nodes whose prerequisites are fully met."""
        completed_ids = {n.node_id for n in self.nodes if n.status == "completed"}
        candidates = []
        for n in self.nodes:
            if n.status != "completed":
                # Check prerequisites
                if all(p in completed_ids for p in n.prerequisites):
                    candidates.append(n)
        return candidates[:count]
