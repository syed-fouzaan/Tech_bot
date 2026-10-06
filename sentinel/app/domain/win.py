"""Work Impact Log (/win): captures measurable accomplishments and appraisal packs."""

from typing import Dict, Any, List, Optional
from sentinel.app.security import scan_for_secrets, redact_secrets


class WorkImpactEngine:
    def format_win_entry(
        self,
        title: str,
        metric_before: Optional[str],
        metric_after: Optional[str],
        impact_summary: str,
    ) -> Dict[str, Any]:
        """
        Validates confidentiality and structures the win entry.
        """
        # Scan for secrets/PII
        combined = f"{title} {metric_before} {metric_after} {impact_summary}"
        is_safe, detected = scan_for_secrets(combined)
        if not is_safe:
            raise ValueError(f"Confidential credentials detected: {', '.join(detected)}. Please abstract company secrets.")

        return {
            "title": title.strip(),
            "metric_before": metric_before.strip() if metric_before else "Metric needed",
            "metric_after": metric_after.strip() if metric_after else "Metric needed",
            "impact_summary": impact_summary.strip(),
            "formatted_star": (
                f"🏆 **Accomplishment**: {title}\n"
                f"• Baseline: {metric_before or 'Unmeasured'}\n"
                f"• Result: {metric_after or 'Completed'}\n"
                f"• Impact: {impact_summary}"
            )
        }

    def generate_appraisal_pack(self, wins: List[Dict[str, Any]]) -> str:
        """
        Compiles logged wins into a structured appraisal/1on1 promotion pack.
        """
        if not wins:
            return "No work wins logged yet. Use `/win <title>` to log your first measurable win!"

        output = ["# 🏢 Work Impact & Promotion Appraisal Pack\n"]
        for idx, w in enumerate(wins, 1):
            output.append(
                f"{idx}. **{w.get('title')}**\n"
                f"   - **Before**: {w.get('metric_before', 'N/A')}\n"
                f"   - **After**: {w.get('metric_after', 'N/A')}\n"
                f"   - **Impact**: {w.get('impact_summary', 'N/A')}\n"
            )
        output.append("💡 *Numbers and outcomes are derived directly from your verified logs.*")
        return "\n".join(output)
