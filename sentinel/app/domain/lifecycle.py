"""Technology Lifecycle states and transition radar."""

from enum import Enum
from typing import Dict, Any


class LifecycleState(str, Enum):
    RESEARCH = "RESEARCH"
    EMERGING = "EMERGING"
    TRENDING = "TRENDING"
    PRODUCTION_READY = "PRODUCTION_READY"
    MATURE = "MATURE"
    DECLINING = "DECLINING"
    DEPRECATED = "DEPRECATED"


def evaluate_lifecycle_state(
    stars: int,
    releases_count: int,
    is_deprecated: bool = False,
    is_paper_only: bool = False,
) -> LifecycleState:
    """Evaluates technology maturity state from empirical signals."""
    if is_deprecated:
        return LifecycleState.DEPRECATED
    if is_paper_only:
        return LifecycleState.RESEARCH
    if releases_count >= 10 and stars >= 5000:
        return LifecycleState.PRODUCTION_READY
    if releases_count >= 3:
        return LifecycleState.TRENDING
    return LifecycleState.EMERGING
