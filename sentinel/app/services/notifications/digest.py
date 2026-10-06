"""Daily brief digest compiler service."""

from typing import List
from sentinel.app.models import ItemModel
from sentinel.app.bot.formatters import format_daily_digest

__all__ = ["format_daily_digest"]
