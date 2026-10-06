"""Career growth ladder and competency gap analysis."""

from typing import Dict, List, Any


class CareerGrowthService:
    def get_ladder_gap_analysis(self) -> List[Dict[str, Any]]:
        return [
            {
                "competency": "Data pipeline rigor",
                "current_level": 3,
                "target_level": 4,
                "gap": -1,
                "action": "Add data quality contracts and alerts to core production DAG.",
            },
            {
                "competency": "Production LLM ops",
                "current_level": 2,
                "target_level": 4,
                "gap": -2,
                "action": "Deploy self-hosted vLLM instance with latency & memory evals.",
            },
            {
                "competency": "System design",
                "current_level": 2,
                "target_level": 3,
                "gap": -1,
                "action": "Author technical RFC on multi-turn agent tool routing.",
            },
        ]
