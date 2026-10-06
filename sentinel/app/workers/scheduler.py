"""Async worker scheduler for periodic tasks and exact 10:00 AM daily brief delivery."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sentinel.app.config import get_settings
from sentinel.app.workers.tasks import run_scheduled_ingestion
from sentinel.app.db.session import async_session_maker
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.services.ingestion.service import IngestionService

logger = logging.getLogger("sentinel.scheduler")


class BackgroundScheduler:
    def __init__(self, interval_hours: int = 4):
        self.interval_seconds = interval_hours * 3600
        self._running = False
        self._task = None
        self._last_delivered_date: Optional[str] = None

    async def _send_daily_10am_brief(self):
        """Generates and pushes the morning brief to Telegram at exact 10:00 AM IST."""
        from sentinel.app.api.telegram import bot
        settings = get_settings()
        if not bot or not settings.ALLOWED_TELEGRAM_USER_IDS:
            return

        cmd_handler = BotCommandHandler()
        ingestion = IngestionService()

        async with async_session_maker() as session:
            try:
                logger.info("Running 10:00 AM scheduled intelligence ingestion...")
                await ingestion.ingest_and_process(session, limit=8)
                digest = await cmd_handler.handle_today(session, user_id=settings.ALLOWED_TELEGRAM_USER_IDS[0])
            except Exception as e:
                logger.error("Error generating 10:00 AM brief: %s", e)
                return

        for user_id in settings.ALLOWED_TELEGRAM_USER_IDS:
            try:
                logger.info("Delivering exact 10:00 AM intelligence brief to Telegram user %s", user_id)
                await bot.send_message(chat_id=user_id, text=digest, parse_mode="HTML")
            except Exception as e:
                logger.error("Failed to deliver 10:00 AM brief to user %s: %s", user_id, e)

    async def _loop(self):
        settings = get_settings()
        delivery_time = getattr(settings, "DIGEST_DELIVERY_TIME_IST", "10:00")
        last_ingestion_time = 0

        while self._running:
            try:
                now_utc = datetime.now(timezone.utc)
                now_ist = now_utc + timedelta(hours=5, minutes=30)
                current_time_str = now_ist.strftime("%H:%M")
                current_date_str = now_ist.strftime("%Y-%m-%d")

                # Check if it is exact 10:00 AM IST and hasn't been delivered today
                if current_time_str == delivery_time and self._last_delivered_date != current_date_str:
                    logger.info("⏰ Triggering scheduled %s IST morning brief!", delivery_time)
                    await self._send_daily_10am_brief()
                    self._last_delivered_date = current_date_str

                # Periodic background ingestion every interval_seconds
                now_timestamp = now_utc.timestamp()
                if now_timestamp - last_ingestion_time >= self.interval_seconds:
                    await run_scheduled_ingestion()
                    last_ingestion_time = now_timestamp

            except Exception as e:
                logger.error("Scheduler error: %s", e)

            # Check every 30 seconds to catch exact 10:00 AM minute
            await asyncio.sleep(30)

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

