"""Async worker scheduler for periodic tasks."""

import asyncio
import logging
from sentinel.app.workers.tasks import run_scheduled_ingestion

logger = logging.getLogger("sentinel.scheduler")


class BackgroundScheduler:
    def __init__(self, interval_hours: int = 4):
        self.interval_seconds = interval_hours * 3600
        self._running = False
        self._task = None

    async def _loop(self):
        while self._running:
            try:
                await run_scheduled_ingestion()
            except Exception as e:
                logger.error("Scheduler error: %s", e)
            await asyncio.sleep(self.interval_seconds)

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
