"""FastAPI Application: Webhook receiver, Health probes, Ingestion trigger, and Metrics."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentinel.app.config import get_settings
from sentinel.app.db.session import init_db
from sentinel.app.api import api_router
from sentinel.app.workers.scheduler import BackgroundScheduler

settings = get_settings()
scheduler = BackgroundScheduler(interval_hours=settings.INGEST_POLL_INTERVAL_HOURS)


import asyncio
import logging
from sentinel.app.api.telegram import bot, dispatcher

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables idempotently
    await init_db()
    # Start background scheduler
    scheduler.start()

    bot_task = None
    if bot:
        try:
            if settings.TELEGRAM_WEBHOOK_URL and settings.TELEGRAM_WEBHOOK_URL.strip():
                wh_url = f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/telegram/webhook/{settings.TELEGRAM_WEBHOOK_SECRET}"
                logger.info("Configuring Telegram Webhook: %s", wh_url)
                await bot.set_webhook(url=wh_url, secret_token=settings.TELEGRAM_WEBHOOK_SECRET, drop_pending_updates=True)
            else:
                logger.info("Configuring Telegram Bot Polling runner in FastAPI...")
                await bot.delete_webhook(drop_pending_updates=True)
                bot_task = asyncio.create_task(dispatcher.start_polling(bot))
        except Exception as e:
            logger.warning("Telegram runner notice: %s", e)

    yield

    if bot_task:
        bot_task.cancel()
    if bot:
        try:
            await bot.session.close()
        except Exception:
            pass
    scheduler.stop()


class HeadMethodMiddleware:
    """Seamlessly handle HTTP HEAD requests for uptime monitors and health checks."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] == "HEAD":
            scope["method"] = "GET"

            async def send_wrapper(message: dict):
                if message["type"] == "http.response.body":
                    await send({**message, "body": b""})
                else:
                    await send(message)

            await self.app(scope, receive, send_wrapper)
            return
        await self.app(scope, receive, send)


app = FastAPI(
    title=settings.APP_NAME,
    version="2.1.0",
    lifespan=lifespan,
)

# Support HEAD requests across all endpoints (e.g. Better Uptime, UptimeRobot, Render)
app.add_middleware(HeadMethodMiddleware)

# Include modular API routers
app.include_router(api_router)
