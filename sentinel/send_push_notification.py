import asyncio
import sys
import os
import logging

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aiogram import Bot
from sentinel.app.config import get_settings
from sentinel.app.db.session import init_db, async_session_maker
from sentinel.app.bot.handlers import BotCommandHandler
from sentinel.app.services.ingestion.service import IngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel.push")


async def push_brief(chat_id: int):
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in sentinel/.env")
        return

    await init_db()
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    cmd_handler = BotCommandHandler()
    ingestion = IngestionService()

    async with async_session_maker() as session:
        # Ingest fresh data if needed
        logger.info("Verifying intelligence index...")
        await ingestion.ingest_and_process(session, limit=5)
        # Generate brief
        digest = await cmd_handler.handle_today(session)

    logger.info(f"Sending brief to Telegram chat_id: {chat_id}...")
    await bot.send_message(chat_id=chat_id, text=digest, parse_mode="HTML")
    logger.info("✅ Brief successfully delivered to Telegram!")
    await bot.session.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_chat = int(sys.argv[1])
    else:
        settings = get_settings()
        if settings.ALLOWED_TELEGRAM_USER_IDS:
            target_chat = settings.ALLOWED_TELEGRAM_USER_IDS[0]
        else:
            logger.error("Usage: python send_push_notification.py <YOUR_TELEGRAM_CHAT_ID>")
            sys.exit(1)

    asyncio.run(push_brief(target_chat))
