"""Spaced Repetition System (SRS) and Daily Quiz Generator."""

import random
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    id: str
    topic: str
    question: str
    options: List[str]
    correct_idx: int
    explanation: str
    prove_it_task: str


QUESTION_BANK: List[QuizQuestion] = [
    QuizQuestion(
        id="q_vllm_paged_attention",
        topic="Inference Optimization",
        question="How does PagedAttention in vLLM reduce GPU VRAM waste compared to traditional KV-caching?",
        options=[
            "By quantizing all attention weights to 1-bit binary values",
            "By allocating KV cache in non-contiguous virtual memory blocks, eliminating external fragmentation",
            "By offloading the entire model weights to system RAM during forward pass",
            "By disabling attention heads for prompts longer than 2048 tokens",
        ],
        correct_idx=1,
        explanation="PagedAttention treats KV cache memory like OS virtual memory paging, preventing pre-allocated contiguous memory bloat and fragmentation.",
        prove_it_task="Deploy a small test instance of vLLM and inspect memory allocation logs with differing batch sizes.",
    ),
    QuizQuestion(
        id="q_awq_vs_gptq",
        topic="Model Quantization",
        question="What is the primary conceptual difference between AWQ (Activation-aware Weight Quantization) and GPTQ?",
        options=[
            "AWQ only quantizes layer norm parameters while GPTQ quantizes embeddings",
            "AWQ protects the top 1% salient weights based on activation magnitudes rather than second-order error gradients",
            "AWQ requires full retraining from scratch with SGD",
            "GPTQ cannot be run on NVIDIA GPUs",
        ],
        correct_idx=1,
        explanation="AWQ identifies that not all weights are equally important: observing activation distributions reveals salient channels that should be protected from quantization distortion.",
        prove_it_task="Compare output perplexity of an AWQ quantized model against standard FP16 on a sample dataset.",
    ),
    QuizQuestion(
        id="q_dbt_incremental",
        topic="Data Engineering & dbt",
        question="In dbt, when is an 'incremental' materialization preferred over a 'table' materialization?",
        options=[
            "When the source table is static and never updates",
            "When the dataset is large and only new or modified rows need transformation to save compute time and cost",
            "When you want to completely drop and recreate the table on every run",
            "When working exclusively with CSV seed files",
        ],
        correct_idx=1,
        explanation="Incremental materializations transform only records created or updated since the last dbt execution, drastically reducing query costs on large datasets.",
        prove_it_task="Write a dbt model with `is_incremental()` conditional logic checking `_loaded_at > max(_loaded_at)`.",
    ),
]


class SRSEngine:
    def __init__(self, bank: Optional[List[QuizQuestion]] = None):
        self.bank = bank or QUESTION_BANK

    def get_daily_quiz(self, count: int = 3) -> List[QuizQuestion]:
        """Returns 3 diverse questions covering AI and Data engineering."""
        sample_size = min(count, len(self.bank))
        return random.sample(self.bank, sample_size)

    def evaluate_answer(self, question_id: str, selected_idx: int) -> Dict[str, Any]:
        for q in self.bank:
            if q.id == question_id:
                is_correct = (selected_idx == q.correct_idx)
                return {
                    "question_id": question_id,
                    "is_correct": is_correct,
                    "correct_option": q.options[q.correct_idx],
                    "explanation": q.explanation,
                    "prove_it_task": q.prove_it_task,
                }
        return {"error": "Question not found"}
