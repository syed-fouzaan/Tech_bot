"""User profile and work context manager."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class WorkContext(BaseModel):
    company_abstract: str = "Growth-stage AI/Data Startup (Bangalore)"
    domain: str = "Data & AI Engineering"
    stack: List[str] = Field(default_factory=lambda: [
        "Python", "SQL", "vLLM", "PyTorch", "Airflow", "dbt", "OpenCV",
        "FastAPI", "PostgreSQL", "LangGraph", "Docker"
    ])
    current_problem_themes: List[str] = Field(default_factory=lambda: [
        "Inference latency optimization", "Data quality testing in pipelines",
        "Reliable multi-turn tool calling", "Self-hosted model memory footprint"
    ])
    confidentiality_mode: str = "abstracted"  # abstracted | private-local | public


class UserProfile(BaseModel):
    name: str = "Syed"
    role: str = "Data and AI Engineer"
    location: str = "Bangalore, India"
    target_role: str = "Senior AI & Data Systems Engineer"
    hardware: Dict[str, Any] = Field(default_factory=lambda: {
        "local_gpu": "RTX 4060 (8GB VRAM)",
        "ram": "32 GB",
        "cpu": "8 cores",
    })
    learning_hours_per_week: int = 6
    work_context: WorkContext = Field(default_factory=WorkContext)
    interests: List[str] = Field(default_factory=lambda: [
        "LLM inference optimization", "Agentic pipelines", "Data platform architecture",
        "Computer vision edge deployment"
    ])
    avoid_list: List[str] = Field(default_factory=lambda: [
        "Blockchain/Crypto", "Proprietary closed wrappers", "Unreproducible social hype"
    ])


def get_default_profile() -> UserProfile:
    """Returns the seed profile for Syed per PRD specifications."""
    return UserProfile()
