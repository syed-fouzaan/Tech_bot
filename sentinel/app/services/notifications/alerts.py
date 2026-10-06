"""Critical advisory and breaking change alert service."""

from typing import Optional
from sentinel.app.models import ItemModel


class AlertService:
    def should_trigger_immediate_alert(self, item: ItemModel) -> bool:
        """Immediate push only for critical CVEs or major breaking changes in registered work stack."""
        is_security = "cve" in item.title.lower() or "security" in item.title.lower()
        is_work_critical = item.priority == "MUST_KNOW" and "day-job" in (item.why_it_matters or "").lower()
        return is_security or is_work_critical
